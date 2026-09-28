import io
from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.constants import REQUIRED_CSV_COLUMNS
from app.models.schemas import UploadSummary
from app.services.db_storage import get_db, get_storage
from app.services.ml import state_slug

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/upload", response_model=UploadSummary)
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse CSV file.")

    missing = [c for c in REQUIRED_CSV_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing)}",
        )

    skip_reasons: list[str] = []
    rows_processed = len(df)

    for col in REQUIRED_CSV_COLUMNS:
        if col in ("state", "year"):
            continue
        if df[col].isna().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    df = df.dropna(subset=["state", "year"])
    rows_skipped = rows_processed - len(df)
    if rows_skipped:
        skip_reasons.append(f"{rows_skipped} rows dropped due to missing state/year")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    storage_path = f"uploads/{timestamp}_{file.filename}"
    bucket = get_storage()
    blob = bucket.blob(storage_path)
    blob.upload_from_string(content, content_type="text/csv")

    db = get_db()
    rows_upserted = 0
    batch = db.batch()
    batch_count = 0

    for _, row in df.iterrows():
        state = str(row["state"]).strip()
        year = int(row["year"])
        doc_id = f"{state_slug(state)}_{year}"
        doc_ref = db.collection("climate_gdp_data").document(doc_id)
        batch.set(
            doc_ref,
            {
                "state": state,
                "year": year,
                "rainfall_mm": float(row["rainfall_mm"]),
                "avg_temperature_c": float(row["avg_temperature_c"]),
                "oni_index": float(row["oni_index"]),
                "agricultural_gdp_cr": float(row["agricultural_gdp_cr"]),
                "created_at": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            },
            merge=True,
        )
        batch_count += 1
        rows_upserted += 1

        if batch_count >= 500:
            batch.commit()
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()

    return UploadSummary(
        rows_processed=rows_processed,
        rows_upserted=rows_upserted,
        rows_skipped=rows_skipped,
        skip_reasons=skip_reasons,
        storage_path=storage_path,
    )

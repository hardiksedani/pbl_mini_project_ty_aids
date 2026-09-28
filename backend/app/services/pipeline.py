import io
import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from app.services.cleaning import clean_panel_data
from app.services.db_storage import get_db, get_storage
from app.services.ingestion.join import download_all_sources
from app.services.ingestion.states import DEFAULT_END_YEAR, DEFAULT_START_YEAR
from app.services.ml import state_slug, train_all_models

logger = logging.getLogger(__name__)


def _upsert_panel(df: pd.DataFrame) -> int:
    """Batch upsert cleaned panel into storage climate_gdp_data."""
    db = get_db()
    batch = db.batch()
    batch_count = 0
    upserted = 0
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

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
                "created_at": now,
                "source": "pipeline",
            },
            merge=True,
        )
        batch_count += 1
        upserted += 1
        if batch_count >= 500:
            batch.commit()
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()
    return upserted


def _archive_cleaned_csv(df: pd.DataFrame) -> str:
    """Archive cleaned panel to storage for audit."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = f"uploads/{timestamp}_pipeline_cleaned.csv"
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    bucket = get_storage()
    blob = bucket.blob(path)
    blob.upload_from_string(csv_bytes, content_type="text/csv")
    return path


def run_full_pipeline(
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
) -> dict[str, Any]:
    """
    End-to-end pipeline: download → clean → store → train all models.
    """
    started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    pipeline_status: dict[str, Any] = {
        "status": "running",
        "started_at": started_at,
        "current_step": "downloading",
    }

    db = get_db()
    db.collection("pipeline_runs").document("current").set(pipeline_status)

    try:
        # Step 1: Download
        raw_panel, source_log = download_all_sources(start_year, end_year)
        pipeline_status["current_step"] = "cleaning"
        pipeline_status["sources"] = source_log
        db.collection("pipeline_runs").document("current").set(pipeline_status, merge=True)

        # Step 2: Clean
        cleaned, cleaning_report = clean_panel_data(raw_panel)
        if cleaned.empty:
            raise ValueError("Cleaning produced empty dataset.")

        storage_path = _archive_cleaned_csv(cleaned)
        cleaning_report["storage_path"] = storage_path

        pipeline_status["current_step"] = "storing"
        pipeline_status["cleaning"] = cleaning_report
        db.collection("pipeline_runs").document("current").set(pipeline_status, merge=True)

        # Step 3: Store in Database
        rows_upserted = _upsert_panel(cleaned)

        pipeline_status["current_step"] = "training"
        pipeline_status["storage"] = {"rows_upserted": rows_upserted}
        db.collection("pipeline_runs").document("current").set(pipeline_status, merge=True)

        # Step 4: Train all models
        training_result = train_all_models()

        completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        result = {
            "status": "completed",
            "started_at": started_at,
            "completed_at": completed_at,
            "current_step": "done",
            "sources": source_log,
            "cleaning": cleaning_report,
            "storage": {"rows_upserted": rows_upserted, "archive_path": storage_path},
            "training": training_result,
        }
        db.collection("pipeline_runs").document("current").set(result)
        logger.info("Pipeline completed successfully")
        return result

    except Exception as exc:
        failed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        error_result = {
            **pipeline_status,
            "status": "failed",
            "failed_at": failed_at,
            "error": str(exc),
        }
        db.collection("pipeline_runs").document("current").set(error_result, merge=True)
        logger.error("Pipeline failed: %s", exc)
        raise


def get_pipeline_status() -> dict[str, Any] | None:
    db = get_db()
    doc = db.collection("pipeline_runs").document("current").get()
    if not doc.exists:
        return None
    return doc.to_dict()

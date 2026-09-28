from fastapi import APIRouter, HTTPException, Response
import io
import json
import pandas as pd

from app.services.ml import (
    fetch_climate_dataframe,
    get_all_model_runs,
    get_model_metrics,
)

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/panel")
async def export_panel_data(format: str = "csv"):
    """Export cleaned panel dataset as CSV or JSON."""
    df = fetch_climate_dataframe()
    if df.empty:
        raise HTTPException(status_code=404, detail="No dataset available for export.")

    if format.lower() == "json":
        return Response(
            content=df.to_json(orient="records", indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=panel_dataset.json"},
        )
    else:
        csv_str = df.to_csv(index=False)
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=panel_dataset.csv"},
        )


@router.get("/metrics")
async def export_metrics(format: str = "json"):
    """Export model comparison metrics and versioned runs."""
    metrics = get_model_metrics()
    runs = get_all_model_runs()
    data = {
        "current_metrics": metrics,
        "all_runs": runs,
    }

    if format.lower() == "csv":
        rows = []
        if metrics and "models" in metrics:
            for m_name, m_val in metrics["models"].items():
                rows.append({
                    "model": m_name,
                    "mae": m_val.get("mae"),
                    "rmse": m_val.get("rmse"),
                    "r2": m_val.get("r2"),
                    "mape": m_val.get("mape"),
                    "training_time_sec": m_val.get("training_time_sec"),
                    "is_best": m_name == metrics.get("best_model"),
                })
        df = pd.DataFrame(rows)
        return Response(
            content=df.to_csv(index=False),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=model_metrics.csv"},
        )
    else:
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=model_metrics.json"},
        )

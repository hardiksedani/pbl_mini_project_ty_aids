import logging
from typing import Any

import pandas as pd

from app.constants import FEATURE_COLUMNS, REQUIRED_CSV_COLUMNS, TARGET_COLUMN

logger = logging.getLogger(__name__)

STATE_ALIASES: dict[str, str] = {
    "NCT of Delhi": "Delhi",
    "Orissa": "Odisha",
    "U.P.": "Uttar Pradesh",
    "Tamilnadu": "Tamil Nadu",
    "Andhra Pradesh": "Andhra Pradesh",
}

VALID_RANGES = {
    "rainfall_mm": (0, 5000),
    "avg_temperature_c": (-5, 50),
    "oni_index": (-3, 4),
    "agricultural_gdp_cr": (0, 10000),
}


def _normalize_state(name: str) -> str:
    cleaned = str(name).strip().title()
    return STATE_ALIASES.get(cleaned, cleaned)


def clean_panel_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Full cleaning pipeline: validate schema, normalize, dedupe, impute, range-check.
    Returns cleaned DataFrame and a detailed report.
    """
    report: dict[str, Any] = {
        "rows_in": len(df),
        "rows_out": 0,
        "rows_dropped": 0,
        "duplicates_removed": 0,
        "imputed_cells": 0,
        "warnings": [],
        "steps": [],
    }

    if df.empty:
        report["warnings"].append("Input dataframe is empty.")
        return df, report

    # Schema check
    missing_cols = [c for c in REQUIRED_CSV_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns after join: {', '.join(missing_cols)}")

    work = df[REQUIRED_CSV_COLUMNS].copy()
    report["steps"].append("Schema validated")

    # Normalize state names
    work["state"] = work["state"].apply(_normalize_state)
    work["year"] = pd.to_numeric(work["year"], errors="coerce").astype("Int64")
    report["steps"].append("State names normalized")

    # Drop rows missing state/year
    before = len(work)
    work = work.dropna(subset=["state", "year"])
    dropped = before - len(work)
    if dropped:
        report["rows_dropped"] += dropped
        report["warnings"].append(f"{dropped} rows dropped (missing state/year)")

    # Deduplicate state-year pairs (keep last)
    before = len(work)
    work = work.drop_duplicates(subset=["state", "year"], keep="last")
    dupes = before - len(work)
    if dupes:
        report["duplicates_removed"] = dupes
        report["steps"].append(f"Removed {dupes} duplicate state-year rows")

    # Numeric coercion
    numeric_cols = FEATURE_COLUMNS + [TARGET_COLUMN]
    for col in numeric_cols:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    # Median imputation per column
    for col in numeric_cols:
        null_count = work[col].isna().sum()
        if null_count > 0:
            median_val = work[col].median()
            work[col] = work[col].fillna(median_val)
            report["imputed_cells"] += int(null_count)
            report["warnings"].append(f"Imputed {null_count} missing values in {col}")

    if report["imputed_cells"]:
        report["steps"].append(f"Median-imputed {report['imputed_cells']} cells")

    # Range validation — clip outliers to valid bounds
    clipped = 0
    for col, (lo, hi) in VALID_RANGES.items():
        out_of_range = (work[col] < lo) | (work[col] > hi)
        count = int(out_of_range.sum())
        if count:
            work[col] = work[col].clip(lo, hi)
            clipped += count
            report["warnings"].append(f"Clipped {count} out-of-range values in {col}")

    if clipped:
        report["steps"].append(f"Clipped {clipped} out-of-range values")

    # Final drop if any critical nulls remain
    before = len(work)
    work = work.dropna(subset=numeric_cols)
    final_dropped = before - len(work)
    if final_dropped:
        report["rows_dropped"] += final_dropped

    work["year"] = work["year"].astype(int)
    work = work.sort_values(["state", "year"]).reset_index(drop=True)

    report["rows_out"] = len(work)
    report["steps"].append(f"Final panel: {len(work)} rows, {work['state'].nunique()} states")

    logger.info(
        "Cleaning complete: %d → %d rows (%d dropped, %d imputed)",
        report["rows_in"],
        report["rows_out"],
        report["rows_dropped"],
        report["imputed_cells"],
    )
    return work, report

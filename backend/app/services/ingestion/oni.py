import io
import logging
from datetime import datetime, timezone

import httpx
import pandas as pd

logger = logging.getLogger(__name__)

# NOAA Physical Sciences Laboratory — Oceanic Niño Index (monthly)
ONI_URL = "https://psl.noaa.gov/data/correlation/oni.data"


def fetch_oni_annual(start_year: int = 2009, end_year: int = 2023) -> pd.DataFrame:
    """Download ONI from NOAA and aggregate to annual means."""
    logger.info("Fetching ONI index from NOAA: %s", ONI_URL)
    response = httpx.get(ONI_URL, timeout=30.0, follow_redirects=True)
    response.raise_for_status()

    rows: list[dict] = []
    for line in response.text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        try:
            year = int(float(parts[0]))
        except (ValueError, IndexError):
            continue
        if year < start_year or year > end_year:
            continue

        monthly = []
        for val in parts[1:13]:
            try:
                v = float(val)
                if v > -90:
                    monthly.append(v)
            except ValueError:
                continue

        if monthly:
            rows.append({"year": year, "oni_index": round(sum(monthly) / len(monthly), 3)})

    if not rows:
        raise ValueError("No ONI data parsed from NOAA source.")

    df = pd.DataFrame(rows)
    logger.info("ONI: fetched %d annual records (%d–%d)", len(df), df.year.min(), df.year.max())
    return df

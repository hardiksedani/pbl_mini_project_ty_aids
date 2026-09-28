import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from app.services.ingestion.climate import fetch_climate_panel
from app.services.ingestion.gdp import fetch_agricultural_gdp
from app.services.ingestion.oni import fetch_oni_annual
from app.services.ingestion.states import DEFAULT_END_YEAR, DEFAULT_START_YEAR

logger = logging.getLogger(__name__)


def download_all_sources(
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """
    Download from all configured sources and join into a raw panel.
    Returns merged DataFrame and per-source status log.
    """
    source_log: list[dict[str, Any]] = []

    # 1. NOAA ONI
    try:
        oni_df = fetch_oni_annual(start_year, end_year)
        source_log.append(
            {
                "source": "NOAA ONI Index",
                "provider": "NOAA Physical Sciences Laboratory",
                "status": "success",
                "records": len(oni_df),
                "url": "https://psl.noaa.gov/data/correlation/oni.data",
            }
        )
    except Exception as exc:
        source_log.append(
            {
                "source": "NOAA ONI Index",
                "provider": "NOAA",
                "status": "failed",
                "error": str(exc),
            }
        )
        raise

    # 2. Agricultural GDP reference
    try:
        gdp_df = fetch_agricultural_gdp()
        source_log.append(
            {
                "source": "Agricultural GDP",
                "provider": "MOSPI State Accounts (reference panel)",
                "status": "success",
                "records": len(gdp_df),
            }
        )
    except Exception as exc:
        source_log.append(
            {
                "source": "Agricultural GDP",
                "provider": "MOSPI reference",
                "status": "failed",
                "error": str(exc),
            }
        )
        raise

    # 3. Open-Meteo climate (states covered by GDP reference)
    gdp_states = gdp_df["state"].unique().tolist()
    try:
        climate_df = fetch_climate_panel(start_year, end_year, states=gdp_states)
        source_log.append(
            {
                "source": "Rainfall & Temperature",
                "provider": "Open-Meteo Archive API",
                "status": "success",
                "records": len(climate_df),
                "url": "https://archive-api.open-meteo.com/v1/archive",
            }
        )
    except Exception as exc:
        source_log.append(
            {
                "source": "Rainfall & Temperature",
                "provider": "Open-Meteo",
                "status": "failed",
                "error": str(exc),
            }
        )
        raise

    # Join: climate ⨝ GDP on (state, year), then ⨝ ONI on (year)
    panel = climate_df.merge(gdp_df, on=["state", "year"], how="inner")
    panel = panel.merge(oni_df, on="year", how="inner")

    source_log.append(
        {
            "source": "Panel merge",
            "provider": "Internal join",
            "status": "success",
            "records": len(panel),
            "detail": f"Joined {panel['state'].nunique()} states × {panel['year'].nunique()} years",
        }
    )

    logger.info(
        "Download complete: %d rows from %d sources",
        len(panel),
        len(source_log) - 1,
    )
    return panel, source_log

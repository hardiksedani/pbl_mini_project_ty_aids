from fastapi import APIRouter, HTTPException, Query
from app.services.ml import fetch_climate_dataframe

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/gdp")
async def get_gdp_analytics(state: str | None = Query(None)):
    df = fetch_climate_dataframe()
    if df.empty:
        return {"data": []}
    if state:
        df = df[df["state"].str.lower() == state.lower()]

    trend = (
        df.groupby(["year"], as_index=False)["agricultural_gdp_cr"]
        .mean()
        .sort_values("year")
        .to_dict(orient="records")
    )
    return {"data": trend}


@router.get("/rainfall")
async def get_rainfall_analytics(state: str | None = Query(None)):
    df = fetch_climate_dataframe()
    if df.empty:
        return {"data": []}
    if state:
        df = df[df["state"].str.lower() == state.lower()]

    trend = (
        df.groupby(["year"], as_index=False)["rainfall_mm"]
        .mean()
        .sort_values("year")
        .to_dict(orient="records")
    )
    return {"data": trend}


@router.get("/temperature")
async def get_temp_analytics(state: str | None = Query(None)):
    df = fetch_climate_dataframe()
    if df.empty:
        return {"data": []}
    if state:
        df = df[df["state"].str.lower() == state.lower()]

    trend = (
        df.groupby(["year"], as_index=False)["avg_temperature_c"]
        .mean()
        .sort_values("year")
        .to_dict(orient="records")
    )
    return {"data": trend}


@router.get("/enso")
async def get_enso_analytics():
    df = fetch_climate_dataframe()
    if df.empty:
        return {"data": []}

    trend = (
        df.groupby(["year"], as_index=False)["oni_index"]
        .mean()
        .sort_values("year")
        .to_dict(orient="records")
    )
    return {"data": trend}

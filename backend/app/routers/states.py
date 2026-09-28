from collections import defaultdict

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    HistoryRow,
    StateHistoryResponse,
    StateSummary,
    StatesResponse,
    YearGdpPoint,
)
from app.services.db_storage import get_db

router = APIRouter(prefix="/api/states", tags=["states"])


@router.get("", response_model=StatesResponse)
async def list_states():
    db = get_db()
    docs = db.collection("climate_gdp_data").stream()

    by_state: dict[str, list] = defaultdict(list)
    for doc in docs:
        data = doc.to_dict()
        state = data.get("state")
        year = data.get("year")
        gdp = data.get("agricultural_gdp_cr")
        if state and year is not None and gdp is not None:
            by_state[state].append({"year": int(year), "agricultural_gdp_cr": float(gdp)})

    states = []
    for state, points in sorted(by_state.items()):
        points.sort(key=lambda p: p["year"])
        states.append(
            StateSummary(
                state=state,
                trend=[YearGdpPoint(**p) for p in points],
            )
        )

    return StatesResponse(states=states)


@router.get("/{state}/history", response_model=StateHistoryResponse)
async def state_history(state: str):
    db = get_db()
    docs = (
        db.collection("climate_gdp_data")
        .where("state", "==", state)
        .order_by("year")
        .stream()
    )

    history = []
    for doc in docs:
        data = doc.to_dict()
        history.append(
            HistoryRow(
                year=int(data["year"]),
                rainfall_mm=float(data["rainfall_mm"]),
                avg_temperature_c=float(data["avg_temperature_c"]),
                oni_index=float(data["oni_index"]),
                agricultural_gdp_cr=float(data["agricultural_gdp_cr"]),
            )
        )

    if not history:
        raise HTTPException(status_code=404, detail=f"No data found for state: {state}")

    return StateHistoryResponse(state=state, history=history)

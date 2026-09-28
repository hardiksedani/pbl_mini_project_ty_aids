from fastapi import APIRouter, HTTPException

from app.models.schemas import ScenarioRequest, ScenarioResponse
from app.services.scenario_service import PRESET_CONFIGS, run_scenario_simulation

router = APIRouter(prefix="/api/scenario", tags=["scenario"])


@router.get("/presets")
async def get_presets():
    """Return available scenario presets and their meteorological parameters."""
    return {"presets": PRESET_CONFIGS}


@router.post("", response_model=ScenarioResponse)
async def simulate_scenario(body: ScenarioRequest):
    """Run hypothetical El Niño climate scenario simulation across all trained regression models."""
    try:
        result = run_scenario_simulation(body)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Scenario simulation error: {str(exc)}",
        )

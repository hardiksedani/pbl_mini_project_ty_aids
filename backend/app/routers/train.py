from fastapi import APIRouter, HTTPException

from app.models.schemas import TrainResponse
from app.services.ml import train_all_models

router = APIRouter(prefix="/api", tags=["train"])


@router.post("/train", response_model=TrainResponse)
async def train_models():
    try:
        result = train_all_models()
        return TrainResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Training failed. Check server logs for details.",
        )

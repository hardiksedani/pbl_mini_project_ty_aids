import logging
import threading

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models.schemas import PipelineStatusResponse
from app.services.pipeline import get_pipeline_status, run_full_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

_pipeline_lock = threading.Lock()
_is_running = False


def _run_pipeline_background() -> None:
    global _is_running
    try:
        run_full_pipeline()
    except Exception as exc:
        logger.exception("Background pipeline failed: %s", exc)
    finally:
        with _pipeline_lock:
            _is_running = False


@router.post("/run", response_model=PipelineStatusResponse)
async def run_pipeline(background_tasks: BackgroundTasks):
    """Start download → clean → store → train in the background."""
    global _is_running

    with _pipeline_lock:
        if _is_running:
            current = get_pipeline_status()
            if current and current.get("status") == "running":
                raise HTTPException(
                    status_code=409,
                    detail="Pipeline is already running. Check /api/pipeline/status.",
                )
        _is_running = True

    background_tasks.add_task(_run_pipeline_background)

    status = get_pipeline_status()
    if status and status.get("status") == "running":
        return PipelineStatusResponse(**status)

    from datetime import datetime, timezone

    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return PipelineStatusResponse(
        status="running",
        current_step="downloading",
        started_at=started,
        message="Pipeline started. Poll GET /api/pipeline/status for progress.",
    )


@router.get("/status", response_model=PipelineStatusResponse)
async def pipeline_status():
    status = get_pipeline_status()
    if not status:
        return PipelineStatusResponse(
            status="idle",
            message="No pipeline run yet. Trigger POST /api/pipeline/run to begin.",
        )
    return PipelineStatusResponse(**status)

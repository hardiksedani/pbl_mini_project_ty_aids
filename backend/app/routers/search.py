from fastapi import APIRouter, HTTPException

from app.models.schemas import SearchRequest, SearchResponse
from app.services.search_service import answer_search_query

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search_assistant(body: SearchRequest):
    """Two-tier search assistant that classifies query intent and synthesizes grounded answers."""
    if not body.query or not body.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    try:
        response = answer_search_query(body)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search service error: {str(exc)}")

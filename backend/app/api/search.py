from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.search import SearchQuery, SearchResponse
from app.search.service import search_service

router = APIRouter(prefix="/search", tags=["Search & Retrieval"])

@router.post("/candidates", response_model=SearchResponse)
def search_candidates(query: SearchQuery):
    """Executes a structured search against the Candidate index."""
    try:
        return search_service.execute_search(query, target_type="candidate")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs", response_model=SearchResponse)
def search_jobs(query: SearchQuery):
    """Executes a structured search against the Job index."""
    try:
        return search_service.execute_search(query, target_type="job")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match", response_model=SearchResponse)
def hybrid_match(query: SearchQuery):
    """Specialized endpoint that enforces a hybrid SearchStrategy."""
    query.search_type = "hybrid"
    try:
        return search_service.execute_search(query, target_type="candidate")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
def get_suggestions(q: str):
    """Auto-complete suggestions for frontend UIs. (Mocked for now)."""
    return {"suggestions": [f"{q} Developer", f"Senior {q} Engineer"]}

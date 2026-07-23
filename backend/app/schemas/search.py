import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.intelligence import Explanation

# ---------------------------------------------------------
# Query Models
# ---------------------------------------------------------


class NumberRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None


class LocationFilter(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remote: Optional[bool] = None


class SearchQuery(BaseModel):
    """Structured JSON representation of a search query."""

    keywords: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    experience: Optional[NumberRange] = None
    education_levels: List[str] = Field(default_factory=list)
    location: Optional[LocationFilter] = None

    # Execution options
    search_type: str = "hybrid"  # keyword, ontology, hybrid, boolean
    ranking_strategy: str = "default"


# ---------------------------------------------------------
# Search Context
# ---------------------------------------------------------


class SearchMetrics(BaseModel):
    """Analytics for a given search query."""

    query_latency_ms: float = 0.0
    candidate_count_initial: int = 0
    candidate_count_filtered: int = 0
    filter_drop_rate: float = 0.0
    ontology_expansion_count: int = 0
    ranking_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0


class SearchContext(BaseModel):
    """State carrier throughout the search pipeline."""

    query: SearchQuery
    expanded_terms: Dict[str, List[str]] = Field(default_factory=dict)
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
    target_type: str = "candidate"  # candidate, job, project
    metadata: Dict[str, Any] = Field(default_factory=dict)
    metrics: SearchMetrics = Field(default_factory=SearchMetrics)

    _start_time: float = 0.0

    def start_timer(self):
        self._start_time = time.time()

    def end_timer(self):
        self.metrics.query_latency_ms = (time.time() - self._start_time) * 1000


# ---------------------------------------------------------
# Search Results
# ---------------------------------------------------------


class SearchResult(BaseModel):
    """Dedicated response model for search items."""

    target_id: str
    target_type: str
    match_score: float
    ranking_score: float
    highlighted_fields: Dict[str, List[str]] = Field(default_factory=dict)
    matched_entities: List[str] = Field(default_factory=list)
    ontology_expansions_used: List[str] = Field(default_factory=list)
    confidence: float
    explanations: List[Explanation] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Top-level search API response payload."""

    results: List[SearchResult]
    total_found: int
    context: SearchContext

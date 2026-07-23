from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Core Abstractions
# ---------------------------------------------------------


class Explanation(BaseModel):
    """Reusable model for explainability across all intelligence modules."""

    category: str
    matched_entities: List[str] = Field(default_factory=list)
    missing_entities: List[str] = Field(default_factory=list)
    weighted_contribution: float = 0.0
    confidence: float = 0.0
    reason: str
    evidence: str


class FeatureVector(BaseModel):
    """Normalized feature vector replacing nested profile documents."""

    skills: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)

    # Aggregated metrics
    years_experience: float = 0.0
    education_level: str = "none"  # e.g. "bachelors", "masters"
    certifications: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    leadership_score: float = 0.0
    project_complexity_score: float = 0.0
    technology_focus: str = "generalist"


# ---------------------------------------------------------
# Domain Profiles
# ---------------------------------------------------------


class CandidateProfile(BaseModel):
    """Standardized abstraction of a parsed Candidate Document (e.g. Resume)."""

    candidate_id: str
    raw_data: Dict[str, Any]  # Extracted JSON
    vector: FeatureVector


class JobProfile(BaseModel):
    """Standardized abstraction of a parsed Job Document."""

    job_id: str
    raw_data: Dict[str, Any]
    required_vector: FeatureVector
    preferred_vector: Optional[FeatureVector] = None


# ---------------------------------------------------------
# Intelligence Outputs
# ---------------------------------------------------------


class MatchResult(BaseModel):
    """Identifies matches between vectors without final scoring."""

    candidate_id: str
    job_id: str
    matched_features: FeatureVector
    missing_features_required: FeatureVector
    missing_features_preferred: FeatureVector
    explanations: List[Explanation] = Field(default_factory=list)


class ScoreResult(BaseModel):
    """Contains final weighted scores derived from a MatchResult."""

    candidate_id: str
    job_id: str
    overall_score: float
    category_scores: Dict[str, float]
    explanations: List[Explanation] = Field(default_factory=list)


class Insight(BaseModel):
    """Represents a structured heuristic insight."""

    title: str
    description: str
    category: str  # e.g., "Strength", "Weakness", "Risk"
    evidence: str


class GapAnalysis(BaseModel):
    """Delta between a candidate and a job requirement."""

    candidate_id: str
    job_id: str
    missing_critical_skills: List[str]
    missing_preferred_skills: List[str]
    experience_gap_years: float = 0.0
    education_gap: bool = False


class Recommendation(BaseModel):
    """Deterministic, actionable step to close a gap."""

    gap_type: str  # e.g. "skill", "certification"
    action: str
    estimated_score_improvement: float
    reason: str


class RankedItem(BaseModel):
    target_id: str
    score: float
    reason: str


class RankingResult(BaseModel):
    """Generic ranked list with contextual reasons."""

    ranking_context: str  # e.g., "Candidates for Job 123"
    rankings: List[RankedItem] = Field(default_factory=list)

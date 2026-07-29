"""Domain models for Phase 3: Deterministic Resume Scoring Engine.

Defines typed Enums, ScoreTraceItem, SectionScore, and canonical ResumeScore models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ScoringCategory(str, Enum):
    """Categorical dimensions of resume scoring."""

    CONTACT_STRUCTURE = "contact_structure"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    SKILLS = "skills"
    WRITING_QUALITY = "writing_quality"


class ScoreDeltaType(str, Enum):
    """Type of point adjustment."""

    BONUS = "bonus"
    DEDUCTION = "deduction"


class ScoreTraceItem(BaseModel):
    """Traceable, audit-ready point delta tied to a stable rule ID."""

    rule_id: str
    category: ScoringCategory
    delta_type: ScoreDeltaType
    points: float
    reason: str


class SectionScore(BaseModel):
    """Section-level raw score, weight, and trace history."""

    category: ScoringCategory
    raw_score: float  # Capped 0 - 100
    weight: float  # e.g., 0.25
    weighted_score: float  # raw_score * weight
    traces: List[ScoreTraceItem] = Field(default_factory=list)


class ResumeScore(BaseModel):
    """Canonical ResumeScore model representing the complete, explainable 0-100 score."""

    candidate_id: str
    resume_id: str
    overall_score: float  # Capped 0 - 100 aggregated weighted score
    section_scores: Dict[str, SectionScore] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    traces: List[ScoreTraceItem] = Field(default_factory=list)
    confidence: float = 1.0
    scoring_version: str = "3.0.0"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

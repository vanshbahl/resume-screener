"""Domain models for Phase 2: Resume Intelligence Engine.

Defines the canonical ``CandidateProfile`` and supporting detail models.
This profile serves as the single source of truth for resume understanding.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProjectDetail(BaseModel):
    """Detailed understanding of a candidate project."""

    name: str
    complexity: str = "Medium"  # "Low", "Medium", "High", "Enterprise"
    technical_depth: str = ""
    business_impact: Optional[str] = None
    scale: str = "Medium"  # "Small", "Medium", "Large Scale", "Distributed"
    modernity: str = "Modern"  # "Legacy", "Modern", "Cutting-Edge"
    tech_stack_maturity: str = "Intermediate"  # "Basic", "Intermediate", "Production-Grade"


class ExperienceSummary(BaseModel):
    """Analytical summary of candidate work experience."""

    total_years_experience: float = 0.0
    relevant_years_experience: float = 0.0
    growth_trajectory: str = "Steady"  # "Accelerated", "Steady", "Stagnant", "Transitioning"
    responsibility_level: str = "Individual Contributor"  # "Individual Contributor", "Tech Lead", "Manager"
    leadership_evidence: List[str] = Field(default_factory=list)
    technical_progression: str = ""


class EducationSummary(BaseModel):
    """Analytical summary of candidate education."""

    highest_qualification: str = "bachelors"  # "bachelors", "masters", "phd", "diploma", "high_school"
    education_stream: str = "General"  # e.g. "Computer Science", "Electrical Eng", "Business"
    graduation_status: str = "Completed"  # "Completed", "In Progress", "Unknown"
    institutions: List[str] = Field(default_factory=list)


class DetectedGap(BaseModel):
    """Structured representation of a detected resume gap or missing metadata."""

    gap_type: str  # "missing_link", "missing_metrics", "employment_gap", "missing_dates"
    severity: str = "warning"  # "warning", "info", "critical"
    description: str


class CandidateProfile(BaseModel):
    """Canonical CandidateProfile: The single source of truth for resume understanding."""

    candidate_id: str
    resume_id: str

    # 1. Classification & Domains
    primary_domain: str = "General Software Engineering"
    secondary_domains: List[str] = Field(default_factory=list)
    career_stage: str = "Mid-level"  # "Entry-level", "Mid-level", "Senior", "Lead"
    education_stream: str = "General"
    current_experience_level: str = "Mid"  # "Junior", "Mid", "Senior", "Principal"
    target_roles: List[str] = Field(default_factory=list)
    industry: str = "Technology"
    seniority: str = "Mid-Level"
    technical_specialization: str = ""

    # 2. Normalized Entities
    normalized_skills: List[str] = Field(default_factory=list)
    normalized_technologies: List[str] = Field(default_factory=list)
    normalized_companies: List[str] = Field(default_factory=list)
    normalized_institutions: List[str] = Field(default_factory=list)
    normalized_certifications: List[str] = Field(default_factory=list)

    # 3. Structural Understandings
    projects: List[ProjectDetail] = Field(default_factory=list)
    experience_summary: ExperienceSummary = Field(default_factory=ExperienceSummary)
    education_summary: EducationSummary = Field(default_factory=EducationSummary)

    # 4. Qualitative Summaries & Gaps
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    detected_gaps: List[DetectedGap] = Field(default_factory=list)

    # 5. Metadata
    engine_version: str = "2.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)

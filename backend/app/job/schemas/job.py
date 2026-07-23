from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Notes
# ---------------------------------------------------------
class JobNoteCreate(BaseModel):
    content: str
    visibility: str = "public"


class JobNoteResponse(BaseModel):
    id: int
    job_id: str
    content: str
    author: str
    visibility: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Timeline
# ---------------------------------------------------------
class JobTimelineResponse(BaseModel):
    id: int
    job_id: str
    event_type: str
    details: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Job Descriptions
# ---------------------------------------------------------
class JobDescriptionResponse(BaseModel):
    id: str
    job_id: str
    is_active: bool
    filename: str
    parser_version: Optional[str] = None
    created_at: datetime
    # We do NOT return the full parsed_metadata here

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Candidates Association
# ---------------------------------------------------------
class JobCandidateAssociationResponse(BaseModel):
    id: int
    job_id: str
    candidate_id: str
    association_status: str
    match_score: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Jobs
# ---------------------------------------------------------
class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    employment_type: str = "full_time"
    location: Optional[str] = None
    salary_range: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class JobStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None


class JobTagsUpdate(BaseModel):
    tags: List[str]


class HiringTeamUpdate(BaseModel):
    hiring_team: Dict[str, Any]  # e.g. {"manager": "uuid", "recruiters": []}


class JobResponse(BaseModel):
    id: str
    title: str
    department: Optional[str]
    employment_type: str
    location: Optional[str]
    salary_range: Optional[str]
    status: str
    hiring_team: Dict[str, Any]
    tags: List[str]
    custom_fields: Dict[str, Any]
    audit_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    descriptions: List[JobDescriptionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}

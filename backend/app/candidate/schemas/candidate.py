from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Notes
# ---------------------------------------------------------
class CandidateNoteCreate(BaseModel):
    content: str
    visibility: str = "public"


class CandidateNoteResponse(BaseModel):
    id: int
    candidate_id: str
    content: str
    author: str
    visibility: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Timeline
# ---------------------------------------------------------
class CandidateTimelineResponse(BaseModel):
    id: int
    candidate_id: str
    event_type: str
    details: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Attachments
# ---------------------------------------------------------
class CandidateAttachmentResponse(BaseModel):
    id: str
    candidate_id: str
    attachment_type: str
    filename: str
    metadata_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Resumes
# ---------------------------------------------------------
class CandidateResumeResponse(BaseModel):
    id: str
    candidate_id: str
    is_active: bool
    filename: str
    parser_version: Optional[str] = None
    created_at: datetime
    # We do NOT return the full parsed_metadata here to keep responses light.
    # It can be fetched via a dedicated /parsed endpoint if needed.

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Candidates
# ---------------------------------------------------------
class CandidateCreate(BaseModel):
    # To create a candidate, we might start empty or with custom fields
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class CandidateUpdate(BaseModel):
    custom_fields: Optional[Dict[str, Any]] = None


class CandidateStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None


class CandidateTagsUpdate(BaseModel):
    tags: List[str]


class CandidateResponse(BaseModel):
    id: str
    status: str
    tags: List[str]
    custom_fields: Dict[str, Any]
    audit_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    # Nested lists to provide a rich Candidate Entity
    resumes: List[CandidateResumeResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}

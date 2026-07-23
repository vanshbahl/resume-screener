from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------
# Template Schemas
# ---------------------------------------------------------
class InterviewTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    interview_type: str
    duration_minutes: int = 60
    default_panel_roles: List[str] = Field(default_factory=list)
    default_criteria: Dict[str, Any] = Field(default_factory=dict)

class InterviewTemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    interview_type: str
    duration_minutes: int
    default_panel_roles: List[str]
    default_criteria: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

# ---------------------------------------------------------
# Schedule Schemas
# ---------------------------------------------------------
class ScheduleCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    location: Optional[str] = None
    meeting_url: Optional[str] = None

    @field_validator("end_time")
    def check_end_time(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class ScheduleResponse(BaseModel):
    id: str
    interview_id: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    timezone: str
    location: Optional[str]
    meeting_url: Optional[str]
    
    model_config = {"from_attributes": True}

# ---------------------------------------------------------
# Panel Schemas
# ---------------------------------------------------------
class PanelMemberCreate(BaseModel):
    user_id: str
    role: str

class PanelMemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    attendance_status: str
    
    model_config = {"from_attributes": True}

# ---------------------------------------------------------
# Feedback & Scorecard Schemas
# ---------------------------------------------------------
class ScorecardCreate(BaseModel):
    criteria: Dict[str, Any]

class ScorecardResponse(BaseModel):
    id: str
    criteria: Dict[str, Any]
    
    model_config = {"from_attributes": True}

class FeedbackSubmit(BaseModel):
    overall_recommendation: str
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    private_notes: Optional[str] = None
    scorecard: Optional[ScorecardCreate] = None

class FeedbackResponse(BaseModel):
    id: str
    user_id: str
    overall_recommendation: Optional[str]
    strengths: Optional[str]
    weaknesses: Optional[str]
    private_notes: Optional[str]
    submitted_at: Optional[datetime]
    scorecard: Optional[ScorecardResponse]
    
    model_config = {"from_attributes": True}

# ---------------------------------------------------------
# Interview Schemas
# ---------------------------------------------------------
class InterviewCreate(BaseModel):
    candidate_id: str
    job_id: str
    workflow_id: Optional[str] = None
    template_id: Optional[str] = None
    title: str
    interview_type: str

class InterviewUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    outcome: Optional[str] = None

class InterviewResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    workflow_id: Optional[str]
    template_id: Optional[str]
    title: str
    interview_type: str
    status: str
    outcome: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    schedule: Optional[ScheduleResponse] = None
    panel: List[PanelMemberResponse] = Field(default_factory=list)
    feedback: List[FeedbackResponse] = Field(default_factory=list)
    
    model_config = {"from_attributes": True}

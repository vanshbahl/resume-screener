from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Pipeline Stage
# ---------------------------------------------------------
class PipelineStageCreate(BaseModel):
    name: str
    order: int
    requires_approval: bool = False
    is_terminal: bool = False


class PipelineStageResponse(BaseModel):
    id: str
    pipeline_id: str
    name: str
    order: int
    requires_approval: bool
    is_terminal: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Pipeline
# ---------------------------------------------------------
class PipelineCreate(BaseModel):
    name: str
    job_id: Optional[str] = None
    is_template: bool = False
    stages: List[PipelineStageCreate]


class PipelineResponse(BaseModel):
    id: str
    name: str
    is_template: bool
    job_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    stages: List[PipelineStageResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Timeline
# ---------------------------------------------------------
class WorkflowTimelineResponse(BaseModel):
    id: int
    workflow_id: str
    event_type: str
    details: Dict[str, Any]
    user_id: Optional[str]
    timestamp: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Approvals and Assignments
# ---------------------------------------------------------
class ApprovalRequest(BaseModel):
    status: str  # approved, rejected
    reason: Optional[str] = None
    approver_id: str


class ApprovalResponse(BaseModel):
    id: int
    workflow_id: str
    stage_id: str
    status: str
    approver_id: Optional[str]
    reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssignmentRequest(BaseModel):
    user_id: str
    role: str


class AssignmentResponse(BaseModel):
    id: int
    workflow_id: str
    stage_id: str
    user_id: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------
# Workflow Instance
# ---------------------------------------------------------
class WorkflowInstanceCreate(BaseModel):
    job_id: str
    candidate_id: str
    pipeline_id: str


class WorkflowTransition(BaseModel):
    target_stage_id: Optional[str] = None
    action: str  # forward, skip, reject, withdraw
    reason: Optional[str] = None
    user_id: str


class WorkflowInstanceResponse(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    pipeline_id: str
    current_stage_id: Optional[str]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    timeline: List[WorkflowTimelineResponse] = Field(default_factory=list)
    approvals: List[ApprovalResponse] = Field(default_factory=list)
    assignments: List[AssignmentResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}

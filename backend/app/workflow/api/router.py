from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.workflow.repositories.workflow import pipeline_repo, workflow_repo
from app.workflow.schemas.workflow import (ApprovalRequest, ApprovalResponse,
                                           AssignmentRequest,
                                           AssignmentResponse, PipelineResponse,
                                           WorkflowInstanceCreate,
                                           WorkflowInstanceResponse,
                                           WorkflowTimelineResponse,
                                           WorkflowTransition)
from app.workflow.services.approval_service import approval_service
from app.workflow.services.assignment_service import assignment_service
from app.workflow.services.pipeline_service import pipeline_service
from app.workflow.services.timeline_service import timeline_service
from app.workflow.services.workflow_service import workflow_service

router = APIRouter(prefix="/workflows", tags=["Workflow Engine"])


# --- Pipelines ---
@router.post("/pipelines", response_model=PipelineResponse)
def create_pipeline(
    template_name: str, job_id: str = None, db: Session = Depends(get_db)
):
    try:
        return pipeline_service.create_pipeline_from_template(db, template_name, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pipelines", response_model=List[PipelineResponse])
def get_pipelines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return pipeline_repo.get_multi(db, skip=skip, limit=limit)


# --- Workflows ---
@router.post("/", response_model=WorkflowInstanceResponse)
def start_workflow(request: WorkflowInstanceCreate, db: Session = Depends(get_db)):
    try:
        return workflow_service.start_workflow(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[WorkflowInstanceResponse])
def get_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return workflow_repo.get_multi(db, skip=skip, limit=limit)


@router.get("/{workflow_id}", response_model=WorkflowInstanceResponse)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    workflow = workflow_repo.get(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.post("/{workflow_id}/transition", response_model=WorkflowInstanceResponse)
def transition_workflow(
    workflow_id: str, transition: WorkflowTransition, db: Session = Depends(get_db)
):
    try:
        return workflow_service.transition_workflow(db, workflow_id, transition)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/approve", response_model=ApprovalResponse)
def approve_stage(
    workflow_id: str, request: ApprovalRequest, db: Session = Depends(get_db)
):
    try:
        return approval_service.process_approval(db, workflow_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/assign", response_model=AssignmentResponse)
def assign_stage(
    workflow_id: str, request: AssignmentRequest, db: Session = Depends(get_db)
):
    try:
        return assignment_service.assign_user(db, workflow_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workflow_id}/timeline", response_model=List[WorkflowTimelineResponse])
def get_workflow_timeline(workflow_id: str, db: Session = Depends(get_db)):
    return timeline_service.get_workflow_timeline(db, workflow_id)

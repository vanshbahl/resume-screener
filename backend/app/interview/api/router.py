from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.interview.schemas.interview import (
    InterviewCreate, InterviewUpdate, InterviewResponse,
    ScheduleCreate, ScheduleResponse, PanelMemberCreate, PanelMemberResponse,
    FeedbackSubmit, FeedbackResponse
)

from app.interview.services.interview_service import InterviewService
from app.interview.services.scheduling_service import SchedulingService
from app.interview.services.evaluation_service import EvaluationService
from app.interview.services.panel_service import PanelService

router = APIRouter(prefix="/interviews", tags=["Interview Management"])

# Mock User ID for auth bypass
FAKE_USER_ID = "recruiter_001"

@router.post("", response_model=InterviewResponse)
def create_interview(data: InterviewCreate, db: Session = Depends(get_db)):
    svc = InterviewService(db)
    return svc.create_interview(data, FAKE_USER_ID)

@router.get("/{interview_id}", response_model=InterviewResponse)
def get_interview(interview_id: str, db: Session = Depends(get_db)):
    svc = InterviewService(db)
    interview = svc.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.patch("/{interview_id}", response_model=InterviewResponse)
def update_interview(interview_id: str, data: InterviewUpdate, db: Session = Depends(get_db)):
    svc = InterviewService(db)
    interview = svc.update_interview(interview_id, data, FAKE_USER_ID)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.post("/{interview_id}/schedule", response_model=ScheduleResponse)
def schedule_interview(interview_id: str, data: ScheduleCreate, db: Session = Depends(get_db)):
    svc = SchedulingService(db)
    return svc.schedule_interview(interview_id, data, FAKE_USER_ID)

@router.post("/{interview_id}/panel", response_model=PanelMemberResponse)
def add_panel_member(interview_id: str, data: PanelMemberCreate, db: Session = Depends(get_db)):
    svc = PanelService(db)
    return svc.add_panel_member(interview_id, data)

@router.delete("/{interview_id}/panel/{user_id}")
def remove_panel_member(interview_id: str, user_id: str, db: Session = Depends(get_db)):
    svc = PanelService(db)
    if not svc.remove_panel_member(interview_id, user_id):
        raise HTTPException(status_code=404, detail="Panel member not found")
    return {"status": "success"}

@router.post("/{interview_id}/feedback", response_model=FeedbackResponse)
def submit_feedback(interview_id: str, data: FeedbackSubmit, db: Session = Depends(get_db)):
    svc = EvaluationService(db)
    return svc.submit_feedback(interview_id, FAKE_USER_ID, data)

@router.post("/{interview_id}/complete", response_model=InterviewResponse)
def complete_interview(interview_id: str, outcome: str, db: Session = Depends(get_db)):
    svc = InterviewService(db)
    interview = svc.complete_interview(interview_id, outcome, FAKE_USER_ID)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

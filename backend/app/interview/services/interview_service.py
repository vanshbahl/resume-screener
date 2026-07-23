from typing import Optional
from sqlalchemy.orm import Session
from app.interview.repositories.interview import InterviewRepository
from app.interview.models.interview import Interview
from app.interview.schemas.interview import InterviewCreate, InterviewUpdate
from app.workflow.services.timeline_service import TimelineService
from app.workflow.schemas.workflow import WorkflowTransition
from app.workflow.services.workflow_service import WorkflowService
import json

class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InterviewRepository(db)
        self.timeline_svc = TimelineService()
        self.workflow_svc = WorkflowService()

    def get_interview(self, interview_id: str) -> Optional[Interview]:
        return self.repo.get_interview(interview_id)

    def create_interview(self, data: InterviewCreate, user_id: str) -> Interview:
        interview = self.repo.create_interview(data)
        
        # Log to timeline
        if interview.workflow_id:
            self.timeline_svc.log_event(
                db=self.db,
                workflow_id=interview.workflow_id,
                event_type="interview_created",
                user_id=user_id,
                details={"interview_id": interview.id, "title": interview.title, "type": interview.interview_type}
            )
            
        return interview

    def update_interview(self, interview_id: str, data: InterviewUpdate, user_id: str) -> Optional[Interview]:
        interview = self.repo.update_interview(interview_id, data)
        if not interview:
            return None
            
        if interview.workflow_id:
            self.timeline_svc.log_event(
                db=self.db,
                workflow_id=interview.workflow_id,
                event_type="interview_updated",
                user_id=user_id,
                details={"interview_id": interview.id, "updates": data.model_dump(exclude_unset=True)}
            )
            
        return interview

    def complete_interview(self, interview_id: str, outcome: str, user_id: str) -> Optional[Interview]:
        # Outcomes: PASS, STRONG_PASS, FAIL, BORDERLINE, NO_DECISION
        update_data = InterviewUpdate(status="COMPLETED", outcome=outcome)
        interview = self.update_interview(interview_id, update_data, user_id)
        
        if not interview or not interview.workflow_id:
            return interview
            
        # Optional: Sync definitive outcomes back to workflow automatically
        # For this MVP, if the outcome is FAIL, we can auto-reject the candidate.
        if outcome == "FAIL":
            transition = WorkflowTransition(
                action="reject",
                reason=f"Failed Interview: {interview.title}",
                user_id=user_id
            )
            try:
                # Add transition.user_id if not present
                transition.user_id = user_id
                self.workflow_svc.transition_workflow(self.db, interview.workflow_id, transition)
            except ValueError:
                pass # Already rejected or terminal
                
        return interview

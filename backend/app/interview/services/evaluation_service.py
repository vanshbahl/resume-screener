from sqlalchemy.orm import Session
from app.interview.repositories.interview import InterviewRepository
from app.interview.models.interview import InterviewFeedback
from app.interview.schemas.interview import FeedbackSubmit
from app.workflow.services.timeline_service import TimelineService

class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InterviewRepository(db)
        self.timeline_svc = TimelineService()

    def submit_feedback(self, interview_id: str, user_id: str, data: FeedbackSubmit) -> InterviewFeedback:
        feedback = self.repo.submit_feedback(interview_id, user_id, data)
        interview = self.repo.get_interview(interview_id)
        
        if interview and interview.workflow_id:
            self.timeline_svc.log_event(
                db=self.db,
                workflow_id=interview.workflow_id,
                event_type="interview_feedback_submitted",
                user_id=user_id,
                details={
                    "interview_id": interview_id,
                    "overall_recommendation": data.overall_recommendation
                }
            )
            
        return feedback

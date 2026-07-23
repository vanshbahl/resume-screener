from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.interview.models.interview import (
    Interview, InterviewSchedule, InterviewPanel, 
    InterviewFeedback, InterviewScorecard, InterviewTemplate
)
from app.interview.schemas.interview import (
    InterviewCreate, InterviewUpdate, ScheduleCreate, 
    PanelMemberCreate, FeedbackSubmit, InterviewTemplateCreate
)
from datetime import datetime

class InterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Interview CRUD
    # ---------------------------------------------------------
    def get_interview(self, interview_id: str) -> Optional[Interview]:
        return self.db.query(Interview).options(
            joinedload(Interview.schedule),
            joinedload(Interview.panel),
            joinedload(Interview.feedback).joinedload(InterviewFeedback.scorecard)
        ).filter(Interview.id == interview_id).first()

    def get_interviews_for_candidate(self, candidate_id: str) -> List[Interview]:
        return self.db.query(Interview).filter(Interview.candidate_id == candidate_id).all()
        
    def get_interviews_for_job(self, job_id: str) -> List[Interview]:
        return self.db.query(Interview).filter(Interview.job_id == job_id).all()

    def create_interview(self, data: InterviewCreate) -> Interview:
        interview = Interview(**data.model_dump())
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def update_interview(self, interview_id: str, data: InterviewUpdate) -> Optional[Interview]:
        interview = self.get_interview(interview_id)
        if not interview:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(interview, key, value)
            
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def delete_interview(self, interview_id: str) -> bool:
        interview = self.get_interview(interview_id)
        if not interview:
            return False
        self.db.delete(interview)
        self.db.commit()
        return True

    # ---------------------------------------------------------
    # Scheduling
    # ---------------------------------------------------------
    def upsert_schedule(self, interview_id: str, data: ScheduleCreate) -> InterviewSchedule:
        schedule = self.db.query(InterviewSchedule).filter(InterviewSchedule.interview_id == interview_id).first()
        if schedule:
            for k, v in data.model_dump().items():
                setattr(schedule, k, v)
        else:
            schedule = InterviewSchedule(interview_id=interview_id, **data.model_dump())
            self.db.add(schedule)
            
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    # ---------------------------------------------------------
    # Panel
    # ---------------------------------------------------------
    def add_panel_member(self, interview_id: str, data: PanelMemberCreate) -> InterviewPanel:
        member = InterviewPanel(interview_id=interview_id, **data.model_dump())
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member
        
    def remove_panel_member(self, interview_id: str, user_id: str) -> bool:
        member = self.db.query(InterviewPanel).filter(
            InterviewPanel.interview_id == interview_id,
            InterviewPanel.user_id == user_id
        ).first()
        if not member:
            return False
        self.db.delete(member)
        self.db.commit()
        return True

    # ---------------------------------------------------------
    # Feedback & Scorecard
    # ---------------------------------------------------------
    def submit_feedback(self, interview_id: str, user_id: str, data: FeedbackSubmit) -> InterviewFeedback:
        # Update or create
        feedback = self.db.query(InterviewFeedback).filter(
            InterviewFeedback.interview_id == interview_id,
            InterviewFeedback.user_id == user_id
        ).first()
        
        feedback_data = data.model_dump(exclude={"scorecard"}, exclude_unset=True)
        
        if feedback:
            for k, v in feedback_data.items():
                setattr(feedback, k, v)
            feedback.submitted_at = datetime.utcnow()
        else:
            feedback = InterviewFeedback(
                interview_id=interview_id, 
                user_id=user_id, 
                submitted_at=datetime.utcnow(),
                **feedback_data
            )
            self.db.add(feedback)
            self.db.flush() # flush to get feedback.id
            
        if data.scorecard:
            scorecard = self.db.query(InterviewScorecard).filter(InterviewScorecard.feedback_id == feedback.id).first()
            if scorecard:
                scorecard.criteria = data.scorecard.criteria
            else:
                scorecard = InterviewScorecard(feedback_id=feedback.id, criteria=data.scorecard.criteria)
                self.db.add(scorecard)
                
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    # ---------------------------------------------------------
    # Templates
    # ---------------------------------------------------------
    def get_template(self, template_id: str) -> Optional[InterviewTemplate]:
        return self.db.query(InterviewTemplate).filter(InterviewTemplate.id == template_id).first()
        
    def create_template(self, data: InterviewTemplateCreate) -> InterviewTemplate:
        template = InterviewTemplate(**data.model_dump())
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

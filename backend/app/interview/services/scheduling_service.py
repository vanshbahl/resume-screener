from sqlalchemy.orm import Session
from app.interview.repositories.interview import InterviewRepository
from app.interview.models.interview import InterviewSchedule
from app.interview.schemas.interview import ScheduleCreate
from app.workflow.services.timeline_service import TimelineService

class SchedulingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InterviewRepository(db)
        self.timeline_svc = TimelineService()

    def schedule_interview(self, interview_id: str, data: ScheduleCreate, user_id: str) -> InterviewSchedule:
        # In a real app, this might check external calendars (Google Calendar, Outlook) for overlaps.
        # For now, we just validate and save.
        
        schedule = self.repo.upsert_schedule(interview_id, data)
        interview = self.repo.get_interview(interview_id)
        
        if interview and interview.workflow_id:
            self.timeline_svc.log_event(
                db=self.db,
                workflow_id=interview.workflow_id,
                event_type="interview_scheduled",
                user_id=user_id,
                details={
                    "interview_id": interview_id, 
                    "start_time": schedule.start_time.isoformat() if schedule.start_time else None,
                    "location": schedule.location
                }
            )
            
        return schedule

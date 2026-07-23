from sqlalchemy.orm import Session
from app.interview.repositories.interview import InterviewRepository
from app.interview.models.interview import InterviewPanel
from app.interview.schemas.interview import PanelMemberCreate

class PanelService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InterviewRepository(db)

    def add_panel_member(self, interview_id: str, data: PanelMemberCreate) -> InterviewPanel:
        return self.repo.add_panel_member(interview_id, data)
        
    def remove_panel_member(self, interview_id: str, user_id: str) -> bool:
        return self.repo.remove_panel_member(interview_id, user_id)

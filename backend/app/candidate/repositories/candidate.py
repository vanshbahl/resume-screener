from sqlalchemy.orm import Session
from typing import List, Optional
from app.candidate.models.candidate import (
    Candidate, 
    CandidateResume, 
    CandidateTimeline, 
    CandidateNote, 
    CandidateAttachment
)
from app.candidate.repositories.base import BaseRepository

class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self):
        super().__init__(Candidate)

class CandidateResumeRepository(BaseRepository[CandidateResume]):
    def __init__(self):
        super().__init__(CandidateResume)
        
    def get_active_resume(self, db: Session, candidate_id: str) -> Optional[CandidateResume]:
        return db.query(self.model).filter(
            self.model.candidate_id == candidate_id, 
            self.model.is_active == True
        ).first()

    def deactivate_all_for_candidate(self, db: Session, candidate_id: str):
        db.query(self.model).filter(self.model.candidate_id == candidate_id).update({"is_active": False})
        db.commit()

class CandidateTimelineRepository(BaseRepository[CandidateTimeline]):
    def __init__(self):
        super().__init__(CandidateTimeline)
        
    def get_by_candidate(self, db: Session, candidate_id: str) -> List[CandidateTimeline]:
        return db.query(self.model).filter(
            self.model.candidate_id == candidate_id
        ).order_by(self.model.timestamp.desc()).all()

class CandidateNoteRepository(BaseRepository[CandidateNote]):
    def __init__(self):
        super().__init__(CandidateNote)

class CandidateAttachmentRepository(BaseRepository[CandidateAttachment]):
    def __init__(self):
        super().__init__(CandidateAttachment)

# Singleton instances
candidate_repo = CandidateRepository()
resume_repo = CandidateResumeRepository()
timeline_repo = CandidateTimelineRepository()
note_repo = CandidateNoteRepository()
attachment_repo = CandidateAttachmentRepository()

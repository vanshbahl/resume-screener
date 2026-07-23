from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.candidate.repositories.candidate import timeline_repo
from app.candidate.models.candidate import CandidateTimeline

class TimelineService:
    def log_event(self, db: Session, candidate_id: str, event_type: str, details: Dict[str, Any], user_id: Optional[str] = None) -> CandidateTimeline:
        """
        Immutable append-only timeline event.
        """
        return timeline_repo.create(db, {
            "candidate_id": candidate_id,
            "event_type": event_type,
            "details": details,
            "user_id": user_id
        })
        
    def get_candidate_timeline(self, db: Session, candidate_id: str) -> List[CandidateTimeline]:
        return timeline_repo.get_by_candidate(db, candidate_id)

timeline_service = TimelineService()

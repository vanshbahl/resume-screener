from typing import List, Optional
from sqlalchemy.orm import Session
from app.candidate.repositories.candidate import candidate_repo
from app.candidate.models.candidate import Candidate
from app.candidate.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateStatusUpdate, CandidateTagsUpdate
from app.candidate.services.timeline_service import timeline_service

class CandidateService:
    def create_candidate(self, db: Session, candidate_in: CandidateCreate, user_id: Optional[str] = None) -> Candidate:
        obj_in = {}
        if candidate_in.custom_fields:
            obj_in["custom_fields"] = candidate_in.custom_fields
        if candidate_in.tags:
            obj_in["tags"] = candidate_in.tags
            
        candidate = candidate_repo.create(db, obj_in)
        
        timeline_service.log_event(
            db=db,
            candidate_id=candidate.id,
            event_type="candidate_created",
            details={"tags": candidate_in.tags},
            user_id=user_id
        )
        return candidate

    def get_candidate(self, db: Session, candidate_id: str) -> Optional[Candidate]:
        return candidate_repo.get(db, candidate_id)

    def update_candidate(self, db: Session, candidate_id: str, candidate_in: CandidateUpdate, user_id: Optional[str] = None) -> Optional[Candidate]:
        candidate = candidate_repo.get(db, candidate_id)
        if not candidate:
            return None
            
        obj_in = {}
        if candidate_in.custom_fields is not None:
            obj_in["custom_fields"] = candidate_in.custom_fields
            
        updated_candidate = candidate_repo.update(db, candidate, obj_in)
        
        timeline_service.log_event(
            db=db,
            candidate_id=candidate.id,
            event_type="candidate_updated",
            details={"fields_updated": list(obj_in.keys())},
            user_id=user_id
        )
        return updated_candidate

    def update_status(self, db: Session, candidate_id: str, status_update: CandidateStatusUpdate, user_id: Optional[str] = None) -> Optional[Candidate]:
        candidate = candidate_repo.get(db, candidate_id)
        if not candidate:
            return None
            
        old_status = candidate.status
        new_status = status_update.status
        
        if old_status != new_status:
            candidate = candidate_repo.update(db, candidate, {"status": new_status})
            
            timeline_service.log_event(
                db=db,
                candidate_id=candidate.id,
                event_type="status_changed",
                details={"old_status": old_status, "new_status": new_status, "reason": status_update.reason},
                user_id=user_id
            )
        return candidate

    def update_tags(self, db: Session, candidate_id: str, tags_update: CandidateTagsUpdate, user_id: Optional[str] = None) -> Optional[Candidate]:
        candidate = candidate_repo.get(db, candidate_id)
        if not candidate:
            return None
            
        old_tags = candidate.tags or []
        new_tags = tags_update.tags
        
        if old_tags != new_tags:
            candidate = candidate_repo.update(db, candidate, {"tags": new_tags})
            
            timeline_service.log_event(
                db=db,
                candidate_id=candidate.id,
                event_type="tags_updated",
                details={"old_tags": old_tags, "new_tags": new_tags},
                user_id=user_id
            )
        return candidate

candidate_service = CandidateService()

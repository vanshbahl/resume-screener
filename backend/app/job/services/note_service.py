from typing import List, Optional
from sqlalchemy.orm import Session
from app.job.repositories.job import note_repo
from app.job.models.job import JobNote
from app.job.schemas.job import JobNoteCreate
from app.job.services.timeline_service import timeline_service

class NoteService:
    def add_note(self, db: Session, job_id: str, note_in: JobNoteCreate, author: str) -> JobNote:
        note = note_repo.create(db, {
            "job_id": job_id,
            "content": note_in.content,
            "author": author,
            "visibility": note_in.visibility
        })
        
        timeline_service.log_event(
            db=db,
            job_id=job_id,
            event_type="note_added",
            details={"note_id": note.id, "visibility": note.visibility},
            user_id=author
        )
        return note

note_service = NoteService()

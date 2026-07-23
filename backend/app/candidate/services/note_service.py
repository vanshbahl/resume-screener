
from sqlalchemy.orm import Session

from app.candidate.models.candidate import CandidateNote
from app.candidate.repositories.candidate import note_repo
from app.candidate.schemas.candidate import CandidateNoteCreate
from app.candidate.services.timeline_service import timeline_service


class NoteService:
    def add_note(
        self, db: Session, candidate_id: str, note_in: CandidateNoteCreate, author: str
    ) -> CandidateNote:
        note = note_repo.create(
            db,
            {
                "candidate_id": candidate_id,
                "content": note_in.content,
                "author": author,
                "visibility": note_in.visibility,
            },
        )

        timeline_service.log_event(
            db=db,
            candidate_id=candidate_id,
            event_type="note_added",
            details={"note_id": note.id, "visibility": note.visibility},
            user_id=author,
        )
        return note


note_service = NoteService()

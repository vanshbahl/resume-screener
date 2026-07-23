from typing import List, Optional

from sqlalchemy.orm import Session

from app.job.models.job import (Job, JobCandidateAssociation, JobDescription,
                                JobNote, JobTimeline)
from app.job.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    def __init__(self):
        super().__init__(Job)


class JobDescriptionRepository(BaseRepository[JobDescription]):
    def __init__(self):
        super().__init__(JobDescription)

    def get_active_description(
        self, db: Session, job_id: str
    ) -> Optional[JobDescription]:
        return (
            db.query(self.model)
            .filter(self.model.job_id == job_id, self.model.is_active == True)
            .first()
        )

    def deactivate_all_for_job(self, db: Session, job_id: str):
        db.query(self.model).filter(self.model.job_id == job_id).update(
            {"is_active": False}
        )
        db.commit()


class JobTimelineRepository(BaseRepository[JobTimeline]):
    def __init__(self):
        super().__init__(JobTimeline)

    def get_by_job(self, db: Session, job_id: str) -> List[JobTimeline]:
        return (
            db.query(self.model)
            .filter(self.model.job_id == job_id)
            .order_by(self.model.timestamp.desc())
            .all()
        )


class JobNoteRepository(BaseRepository[JobNote]):
    def __init__(self):
        super().__init__(JobNote)

    def get_by_job(self, db: Session, job_id: str) -> List[JobNote]:
        return (
            db.query(self.model)
            .filter(self.model.job_id == job_id)
            .order_by(self.model.created_at.desc())
            .all()
        )


class JobCandidateAssociationRepository(BaseRepository[JobCandidateAssociation]):
    def __init__(self):
        super().__init__(JobCandidateAssociation)

    def get_by_job(self, db: Session, job_id: str) -> List[JobCandidateAssociation]:
        return (
            db.query(self.model)
            .filter(self.model.job_id == job_id)
            .order_by(self.model.created_at.desc())
            .all()
        )


# Singleton instances
job_repo = JobRepository()
job_description_repo = JobDescriptionRepository()
timeline_repo = JobTimelineRepository()
note_repo = JobNoteRepository()
job_candidate_repo = JobCandidateAssociationRepository()

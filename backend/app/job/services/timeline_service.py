from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.job.models.job import JobTimeline
from app.job.repositories.job import timeline_repo


class TimelineService:
    def log_event(
        self,
        db: Session,
        job_id: str,
        event_type: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> JobTimeline:
        """
        Immutable append-only timeline event for Jobs.
        """
        return timeline_repo.create(
            db,
            {
                "job_id": job_id,
                "event_type": event_type,
                "details": details,
                "user_id": user_id,
            },
        )

    def get_job_timeline(self, db: Session, job_id: str) -> List[JobTimeline]:
        return timeline_repo.get_by_job(db, job_id)


timeline_service = TimelineService()

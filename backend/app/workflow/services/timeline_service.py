from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.workflow.models.workflow import WorkflowTimeline
from app.workflow.repositories.workflow import timeline_repo


class TimelineService:
    def log_event(
        self,
        db: Session,
        workflow_id: str,
        event_type: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> WorkflowTimeline:
        """
        Immutable append-only timeline event for Workflows.
        """
        return timeline_repo.create(
            db,
            {
                "workflow_id": workflow_id,
                "event_type": event_type,
                "details": details,
                "user_id": user_id,
            },
        )

    def get_workflow_timeline(
        self, db: Session, workflow_id: str
    ) -> List[WorkflowTimeline]:
        return timeline_repo.get_by_workflow(db, workflow_id)


timeline_service = TimelineService()

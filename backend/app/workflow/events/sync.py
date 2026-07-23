import logging

from sqlalchemy.orm import Session

from app.candidate.services.timeline_service import \
    timeline_service as candidate_timeline_service
from app.job.services.timeline_service import \
    timeline_service as job_timeline_service
from app.workflow.repositories.workflow import (pipeline_stage_repo,
                                                workflow_repo)

logger = logging.getLogger(__name__)


def sync_workflow_event(db: Session, workflow_id: str):
    """
    Called whenever a workflow instance changes state.
    Syncs the event back to the Candidate timeline and Job timeline,
    and updates any search indexing or analytics caches.
    """
    workflow = workflow_repo.get(db, workflow_id)
    if not workflow:
        return

    stage_name = "Unknown"
    if workflow.current_stage_id:
        stage = pipeline_stage_repo.get(db, workflow.current_stage_id)
        if stage:
            stage_name = stage.name

    details = {
        "workflow_id": workflow_id,
        "status": workflow.status,
        "current_stage": stage_name,
    }

    # 1. Sync to Candidate Timeline
    try:
        candidate_timeline_service.log_event(
            db=db,
            candidate_id=workflow.candidate_id,
            event_type="workflow_update",
            details=details,
            user_id="system",
        )
    except Exception as e:
        logger.error(f"Failed to sync workflow {workflow_id} to Candidate: {e}")

    # 2. Sync to Job Timeline
    try:
        job_timeline_service.log_event(
            db=db,
            job_id=workflow.job_id,
            event_type="workflow_update",
            details={"candidate_id": workflow.candidate_id, **details},
            user_id="system",
        )
    except Exception as e:
        logger.error(f"Failed to sync workflow {workflow_id} to Job: {e}")

    # In a full implementation, we would also update `JobCandidateAssociation`
    # and trigger a SearchService index update for the candidate so recruiters
    # can filter by "Candidate currently in Technical Interview"

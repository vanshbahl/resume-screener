from sqlalchemy.orm import Session

from app.workflow.models.workflow import Assignment
from app.workflow.repositories.workflow import assignment_repo, workflow_repo
from app.workflow.schemas.workflow import AssignmentRequest
from app.workflow.services.timeline_service import timeline_service


class AssignmentService:
    def assign_user(
        self, db: Session, workflow_id: str, request: AssignmentRequest
    ) -> Assignment:
        workflow = workflow_repo.get(db, workflow_id)
        if not workflow:
            raise ValueError("Workflow not found")

        if not workflow.current_stage_id:
            raise ValueError("Workflow has no active stage")

        assignment = assignment_repo.create(
            db,
            {
                "workflow_id": workflow_id,
                "stage_id": workflow.current_stage_id,
                "user_id": request.user_id,
                "role": request.role,
            },
        )

        timeline_service.log_event(
            db=db,
            workflow_id=workflow_id,
            event_type="assigned",
            details={
                "stage_id": workflow.current_stage_id,
                "assigned_to": request.user_id,
                "role": request.role,
            },
            user_id="system",
        )

        return assignment


assignment_service = AssignmentService()

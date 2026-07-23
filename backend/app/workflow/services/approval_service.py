
from sqlalchemy.orm import Session

from app.workflow.models.workflow import Approval
from app.workflow.repositories.workflow import approval_repo, workflow_repo
from app.workflow.schemas.workflow import ApprovalRequest
from app.workflow.services.timeline_service import timeline_service


class ApprovalService:
    def process_approval(
        self, db: Session, workflow_id: str, request: ApprovalRequest
    ) -> Approval:
        workflow = workflow_repo.get(db, workflow_id)
        if not workflow:
            raise ValueError("Workflow not found")

        if not workflow.current_stage_id:
            raise ValueError("Workflow has no active stage to approve")

        # Create the approval record
        approval = approval_repo.create(
            db,
            {
                "workflow_id": workflow_id,
                "stage_id": workflow.current_stage_id,
                "status": request.status,
                "approver_id": request.approver_id,
                "reason": request.reason,
            },
        )

        timeline_service.log_event(
            db=db,
            workflow_id=workflow_id,
            event_type="stage_approval",
            details={
                "stage_id": workflow.current_stage_id,
                "status": request.status,
                "reason": request.reason,
            },
            user_id=request.approver_id,
        )

        return approval


approval_service = ApprovalService()

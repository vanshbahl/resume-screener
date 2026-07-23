from sqlalchemy.orm import Session
from app.workflow.services.workflow_service import WorkflowService
from app.workflow.schemas.workflow import WorkflowTransition, WorkflowInstanceResponse

class QuickActionService:
    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(db)

    def advance_workflow(self, pipeline_id: int, to_stage: str, user_id: str) -> bool:
        # Delegates directly to the existing workflow service
        transition = WorkflowTransition(
            target_stage_id=to_stage,
            action="forward",
            reason="Advanced via Recruiter Workspace Quick Action",
            user_id=user_id
        )
        
        instance = self.workflow_service.get_workflow(str(pipeline_id))
        if not instance:
            return False
        
        self.workflow_service.transition_workflow(str(pipeline_id), transition, user_id)
        return True

from typing import List, Optional

from sqlalchemy.orm import Session

from app.workflow.models.workflow import (Approval, Assignment, Pipeline,
                                          PipelineStage, WorkflowInstance,
                                          WorkflowTimeline)
from app.workflow.repositories.base import BaseRepository


class PipelineRepository(BaseRepository[Pipeline]):
    def __init__(self):
        super().__init__(Pipeline)


class PipelineStageRepository(BaseRepository[PipelineStage]):
    def __init__(self):
        super().__init__(PipelineStage)

    def get_stages_for_pipeline(
        self, db: Session, pipeline_id: str
    ) -> List[PipelineStage]:
        return (
            db.query(self.model)
            .filter(self.model.pipeline_id == pipeline_id)
            .order_by(self.model.order.asc())
            .all()
        )


class WorkflowRepository(BaseRepository[WorkflowInstance]):
    def __init__(self):
        super().__init__(WorkflowInstance)

    def get_by_candidate_and_job(
        self, db: Session, candidate_id: str, job_id: str
    ) -> Optional[WorkflowInstance]:
        return (
            db.query(self.model)
            .filter(
                self.model.candidate_id == candidate_id, self.model.job_id == job_id
            )
            .first()
        )


class WorkflowTimelineRepository(BaseRepository[WorkflowTimeline]):
    def __init__(self):
        super().__init__(WorkflowTimeline)

    def get_by_workflow(self, db: Session, workflow_id: str) -> List[WorkflowTimeline]:
        return (
            db.query(self.model)
            .filter(self.model.workflow_id == workflow_id)
            .order_by(self.model.timestamp.desc())
            .all()
        )


class ApprovalRepository(BaseRepository[Approval]):
    def __init__(self):
        super().__init__(Approval)

    def get_by_workflow_and_stage(
        self, db: Session, workflow_id: str, stage_id: str
    ) -> List[Approval]:
        return (
            db.query(self.model)
            .filter(
                self.model.workflow_id == workflow_id, self.model.stage_id == stage_id
            )
            .all()
        )


class AssignmentRepository(BaseRepository[Assignment]):
    def __init__(self):
        super().__init__(Assignment)


# Singleton instances
pipeline_repo = PipelineRepository()
pipeline_stage_repo = PipelineStageRepository()
workflow_repo = WorkflowRepository()
timeline_repo = WorkflowTimelineRepository()
approval_repo = ApprovalRepository()
assignment_repo = AssignmentRepository()

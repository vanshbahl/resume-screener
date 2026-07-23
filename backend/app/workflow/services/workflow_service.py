import os

import yaml
from sqlalchemy.orm import Session

from app.workflow.models.workflow import WorkflowInstance
from app.workflow.repositories.workflow import (approval_repo,
                                                pipeline_stage_repo,
                                                workflow_repo)
from app.workflow.schemas.workflow import (WorkflowInstanceCreate,
                                           WorkflowTransition)
from app.workflow.services.timeline_service import timeline_service


class WorkflowService:
    def __init__(self):
        self.rules = []
        try:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "../../../config/workflow/transition_rules.yaml",
            )
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                self.rules = data.get("global_rules", [])
        except Exception:
            self.rules = []

    def start_workflow(
        self, db: Session, request: WorkflowInstanceCreate
    ) -> WorkflowInstance:
        existing = workflow_repo.get_by_candidate_and_job(
            db, request.candidate_id, request.job_id
        )
        if existing:
            raise ValueError("Workflow already exists for this candidate and job")

        stages = pipeline_stage_repo.get_stages_for_pipeline(db, request.pipeline_id)
        if not stages:
            raise ValueError("Pipeline has no stages")

        first_stage = stages[0]

        workflow = workflow_repo.create(
            db,
            {
                "job_id": request.job_id,
                "candidate_id": request.candidate_id,
                "pipeline_id": request.pipeline_id,
                "current_stage_id": first_stage.id,
                "status": "active",
            },
        )

        timeline_service.log_event(
            db=db,
            workflow_id=workflow.id,
            event_type="workflow_started",
            details={
                "pipeline_id": request.pipeline_id,
                "first_stage_id": first_stage.id,
            },
            user_id="system",
        )

        # Trigger sync
        from app.workflow.events.sync import sync_workflow_event

        sync_workflow_event(db, workflow.id)

        return workflow

    def transition_workflow(
        self, db: Session, workflow_id: str, transition: WorkflowTransition
    ) -> WorkflowInstance:
        workflow = workflow_repo.get(db, workflow_id)
        if not workflow:
            raise ValueError("Workflow not found")

        if workflow.status != "active":
            raise ValueError("Cannot transition a non-active workflow")

        # Validation Rule: no_skip_approval
        no_skip_rule = next(
            (
                r
                for r in self.rules
                if r["type"] == "no_skip_approval" and r.get("enabled")
            ),
            None,
        )
        if no_skip_rule and workflow.current_stage_id:
            current_stage = pipeline_stage_repo.get(db, workflow.current_stage_id)
            if current_stage and current_stage.requires_approval:
                approvals = approval_repo.get_by_workflow_and_stage(
                    db, workflow_id, current_stage.id
                )
                approved = any(a.status == "approved" for a in approvals)
                if not approved:
                    raise ValueError(
                        "Cannot transition: Current stage requires approval"
                    )

        old_stage = workflow.current_stage_id

        if transition.action in ["reject", "withdraw"]:
            workflow = workflow_repo.update(db, workflow, {"status": transition.action})
        else:
            if not transition.target_stage_id:
                raise ValueError("target_stage_id required for forward transitions")

            target_stage = pipeline_stage_repo.get(db, transition.target_stage_id)
            if not target_stage:
                raise ValueError("Target stage not found")

            if target_stage.is_terminal:
                workflow = workflow_repo.update(
                    db,
                    workflow,
                    {
                        "current_stage_id": target_stage.id,
                        "status": "hired",  # Or another terminal status
                    },
                )
            else:
                workflow = workflow_repo.update(
                    db, workflow, {"current_stage_id": target_stage.id}
                )

        timeline_service.log_event(
            db=db,
            workflow_id=workflow_id,
            event_type="transitioned",
            details={
                "action": transition.action,
                "old_stage_id": old_stage,
                "new_stage_id": workflow.current_stage_id,
                "status": workflow.status,
                "reason": transition.reason,
            },
            user_id=transition.user_id,
        )

        # Trigger sync
        from app.workflow.events.sync import sync_workflow_event

        sync_workflow_event(db, workflow.id)

        return workflow


workflow_service = WorkflowService()

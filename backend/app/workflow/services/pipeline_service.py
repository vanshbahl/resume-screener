import os

import yaml
from sqlalchemy.orm import Session

from app.workflow.models.workflow import Pipeline
from app.workflow.repositories.workflow import (pipeline_repo,
                                                pipeline_stage_repo)


class PipelineService:
    def __init__(self):
        self.templates = {}
        try:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "../../../config/workflow/pipeline_templates.yaml",
            )
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                self.templates = data.get("templates", {})
        except Exception:
            self.templates = {}

    def create_pipeline_from_template(
        self, db: Session, template_name: str, job_id: str = None
    ) -> Pipeline:
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")

        template = self.templates[template_name]

        # Create Pipeline
        pipeline = pipeline_repo.create(
            db,
            {
                "name": (
                    f"{template['name']} (Customized)" if job_id else template["name"]
                ),
                "is_template": job_id is None,
                "job_id": job_id,
            },
        )

        # Create Stages
        for stage_def in template.get("stages", []):
            pipeline_stage_repo.create(
                db,
                {
                    "pipeline_id": pipeline.id,
                    "name": stage_def["name"],
                    "order": stage_def["order"],
                    "requires_approval": stage_def.get("requires_approval", False),
                    "is_terminal": stage_def.get("is_terminal", False),
                },
            )

        return pipeline


pipeline_service = PipelineService()

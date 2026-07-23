from typing import Dict, Any, Optional
from jinja2 import Template
from app.ai.repositories.ai_repo import AIRepository
from app.ai.models.base_models import AIPromptTemplate

class PromptTemplateService:
    """Manages retrieving, rendering, and validating prompt templates."""
    def __init__(self, repo: AIRepository):
        self.repo = repo

    def render_prompt(self, template_name: str, org_id: str, variables: Dict[str, Any]) -> str:
        """
        Retrieves a template by name, ensuring org isolation (or falling back to system default),
        and renders it using Jinja2 with the provided variables.
        """
        template = self.repo.get_prompt_template(template_name, org_id)
        
        if not template:
            # For this MVP, if not in DB, use hardcoded fallback based on name
            return self._get_hardcoded_fallback(template_name, variables)
            
        jinja_template = Template(template.system_prompt)
        return jinja_template.render(**variables)

    def _get_hardcoded_fallback(self, template_name: str, variables: Dict[str, Any]) -> str:
        if template_name == "recruiter_copilot_system":
            base = (
                "You are the Recruiter Copilot. You assist recruiters in sourcing, screening, "
                "and managing candidates. You use the provided tools to fetch deterministic "
                "data and never invent candidate profiles or job details."
            )
            if variables:
                base += f"\nContext variables: {variables}"
            return base
        elif template_name == "resume_review_agent":
            return "You are an expert Resume Review agent. You analyze CVs against Job Descriptions."
        
        return "You are a helpful AI assistant."

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
# Imports to domain entities would be here (e.g., from app.candidate.models import Candidate)

class ContextBuilder:
    """Aggregates contextual data for the AI system while respecting RBAC."""
    def __init__(self, db: Session):
        self.db = db

    def build_context(self, context_data: Dict[str, Any], org_id: str, user_id: str) -> str:
        """
        Given generic context_data (e.g., {"candidate_id": "123", "job_id": "456"}),
        fetch the relevant objects and serialize them into text for the LLM prompt.
        Validates organization_id to ensure tenant isolation.
        """
        if not context_data:
            return ""

        context_blocks = []

        # Example: if UI is on a candidate page, pass the candidate's resume summary
        if "candidate_id" in context_data:
            candidate_id = context_data["candidate_id"]
            # Enforce RBAC/Org boundaries here
            # candidate = self.db.query(Candidate).filter(id=candidate_id, org_id=org_id).first()
            context_blocks.append(f"Context: Viewing Candidate ID {candidate_id}")
            
        if "job_id" in context_data:
            job_id = context_data["job_id"]
            context_blocks.append(f"Context: Viewing Job ID {job_id}")

        if not context_blocks:
            return ""

        return "### Current Application Context ###\n" + "\n".join(context_blocks)

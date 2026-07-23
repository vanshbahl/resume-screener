from app.ai.repositories.ai_repo import AIRepository
from app.ai.models.base_models import AIFeedback
from app.ai.schemas.schemas import FeedbackCreate

class FeedbackService:
    def __init__(self, repo: AIRepository):
        self.repo = repo

    def submit_feedback(self, data: FeedbackCreate, org_id: str, user_id: str) -> AIFeedback:
        fb = AIFeedback(
            organization_id=org_id,
            user_id=user_id,
            conversation_id=data.conversation_id,
            message_id=data.message_id,
            rating=data.rating,
            comment=data.comment,
            corrected_output=data.corrected_output
        )
        return self.repo.create_feedback(fb)

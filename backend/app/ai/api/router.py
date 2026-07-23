from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.identity.middleware.auth_middleware import get_current_user
from app.identity.middleware.org_middleware import get_current_organization_id
from app.identity.models.user import User

from app.ai.schemas.schemas import ChatRequest, ChatResponse, ConversationSchema, FeedbackCreate
from app.ai.services.copilot_service import CopilotService
from app.ai.services.feedback_service import FeedbackService
from app.ai.repositories.ai_repo import AIRepository

router = APIRouter(prefix="/ai", tags=["AI Platform"])

@router.post("/chat", response_model=ChatResponse)
def chat_with_copilot(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = CopilotService(db)
    try:
        return service.process_chat(request, str(org_id), str(user.id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/conversations", response_model=List[ConversationSchema])
def list_conversations(
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    repo = AIRepository(db)
    return repo.list_conversations(user_id=str(user.id), org_id=str(org_id), limit=limit)

@router.post("/feedback")
def submit_feedback(
    request: FeedbackCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = FeedbackService(AIRepository(db))
    service.submit_feedback(request, str(org_id), str(user.id))
    return {"status": "Feedback recorded."}

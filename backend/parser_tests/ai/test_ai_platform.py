import pytest
from sqlalchemy.orm import Session
from app.ai.models.base_models import AIConversation, AIPromptTemplate, AITrace, AIMessage
from app.ai.schemas.schemas import ChatRequest, FeedbackCreate
from app.ai.services.copilot_service import CopilotService
from app.ai.services.feedback_service import FeedbackService
from app.ai.repositories.ai_repo import AIRepository
from app.identity.models.user import User
from app.identity.models.organization import Organization
import uuid

def create_test_org_and_user(db_session: Session):
    org = Organization(name="Test Org", slug=f"test_org_{uuid.uuid4().hex[:8]}")
    db_session.add(org)
    db_session.commit()
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        hashed_password="test",
        first_name="Test",
        last_name="User",
        organization_id=org.id
    )
    db_session.add(user)
    db_session.commit()
    return org.id, user.id

def test_create_and_retrieve_prompt_template(db_session: Session):
    repo = AIRepository(db_session)
    org_id, _ = create_test_org_and_user(db_session)
    
    template = AIPromptTemplate(
        organization_id=org_id,
        name="test_prompt",
        version="v1",
        system_prompt="Hello {{ name }}!"
    )
    db_session.add(template)
    db_session.commit()
    
    retrieved = repo.get_prompt_template("test_prompt", org_id)
    assert retrieved is not None
    assert retrieved.system_prompt == "Hello {{ name }}!"

def test_copilot_service_chat(db_session: Session):
    org_id, user_id = create_test_org_and_user(db_session)
    
    service = CopilotService(db_session)
    request = ChatRequest(
        agent_type="recruiter_copilot",
        message="Search for software engineers",
        context_data={"job_id": "job_123"}
    )
    
    response = service.process_chat(request, str(org_id), str(user_id))
    
    assert response.conversation_id is not None
    assert response.message.role == "assistant"
    # The orchestrator will execute the tool and return the final message
    assert "Candidate matching" in response.message.content

def test_feedback_service(db_session: Session):
    org_id, user_id = create_test_org_and_user(db_session)
    repo = AIRepository(db_session)
    
    # Needs conversation & message first
    conv = repo.create_conversation(AIConversation(organization_id=org_id, user_id=user_id, agent_type="test"))
    msg = repo.add_message(AIMessage(conversation_id=conv.id, sequence_number=1, role="user", content="hello"))
    
    service = FeedbackService(repo)
    req = FeedbackCreate(
        conversation_id=conv.id,
        message_id=msg.id,
        rating=1.0,
        comment="Great response!"
    )
    
    fb = service.submit_feedback(req, str(org_id), str(user_id))
    assert fb.id is not None
    assert fb.rating == 1.0
    assert fb.comment == "Great response!"

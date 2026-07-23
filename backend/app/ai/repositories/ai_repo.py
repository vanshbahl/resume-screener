from typing import List, Optional
from sqlalchemy.orm import Session
from app.ai.models.base_models import (
    AIConversation,
    AIMessage,
    AIPromptTemplate,
    AIFeedback,
    AITrace,
    AICost
)

class AIRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Conversation & Messages ---
    def create_conversation(self, conversation: AIConversation) -> AIConversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: str, org_id: str) -> Optional[AIConversation]:
        return self.db.query(AIConversation).filter(
            AIConversation.id == conversation_id,
            AIConversation.organization_id == org_id
        ).first()
        
    def list_conversations(self, user_id: str, org_id: str, limit: int = 20) -> List[AIConversation]:
        return self.db.query(AIConversation).filter(
            AIConversation.user_id == user_id,
            AIConversation.organization_id == org_id
        ).order_by(AIConversation.updated_at.desc()).limit(limit).all()

    def add_message(self, message: AIMessage) -> AIMessage:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Touch conversation updated_at
        conv = self.db.query(AIConversation).filter(AIConversation.id == message.conversation_id).first()
        if conv:
            conv.updated_at = message.created_at
            self.db.commit()
            
        return message
        
    def get_messages(self, conversation_id: str) -> List[AIMessage]:
        return self.db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation_id
        ).order_by(AIMessage.sequence_number.asc()).all()

    # --- Prompt Templates ---
    def get_prompt_template(self, name: str, org_id: str) -> Optional[AIPromptTemplate]:
        # Try org specific, fallback to system (org_id=None)
        template = self.db.query(AIPromptTemplate).filter(
            AIPromptTemplate.name == name,
            AIPromptTemplate.organization_id == org_id,
            AIPromptTemplate.is_active == True
        ).first()
        
        if not template:
            template = self.db.query(AIPromptTemplate).filter(
                AIPromptTemplate.name == name,
                AIPromptTemplate.organization_id.is_(None),
                AIPromptTemplate.is_active == True
            ).first()
            
        return template

    # --- Feedback ---
    def create_feedback(self, feedback: AIFeedback) -> AIFeedback:
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    # --- Traces & Cost ---
    def create_trace(self, trace: AITrace) -> AITrace:
        self.db.add(trace)
        self.db.commit()
        self.db.refresh(trace)
        return trace
        
    def get_trace(self, trace_id: str, org_id: str) -> Optional[AITrace]:
        return self.db.query(AITrace).filter(
            AITrace.id == trace_id,
            AITrace.organization_id == org_id
        ).first()

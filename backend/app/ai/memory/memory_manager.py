from typing import List, Dict, Any
from app.ai.schemas.schemas import Message, Role
from app.ai.repositories.ai_repo import AIRepository
from app.ai.models.base_models import AIMessage

class MemoryManager:
    """Manages short-term and long-term memory for AI conversations."""
    def __init__(self, repo: AIRepository):
        self.repo = repo

    def get_conversation_history(self, conversation_id: str, max_messages: int = 20) -> List[Message]:
        """
        Retrieves the last N messages of a conversation.
        """
        raw_messages = self.repo.get_messages(conversation_id)
        
        # Take the last N messages
        recent_messages = raw_messages[-max_messages:]
        
        history = []
        for rm in recent_messages:
            msg = Message(
                id=rm.id,
                role=Role(rm.role.value),
                content=rm.content,
                tool_calls=[tc for tc in rm.tool_calls] if rm.tool_calls else None,
                tool_call_id=rm.tool_call_id,
                citations=rm.citations
            )
            history.append(msg)
            
        return history

    def summarize_memory(self, conversation_id: str) -> str:
        """
        Stub for long-term memory summarization.
        Would take older messages and pass them to an LLM to generate a dense summary.
        """
        return "Memory summary not implemented."

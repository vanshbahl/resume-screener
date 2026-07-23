from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.ai.repositories.ai_repo import AIRepository
from app.ai.memory.memory_manager import MemoryManager
from app.ai.memory.context_builder import ContextBuilder
from app.ai.prompts.prompt_manager import PromptTemplateService
from app.ai.tools.registry import ToolRegistry
from app.ai.agents.copilots import RecruiterCopilot
from app.ai.providers.mock import MockLLMProvider
from app.ai.schemas.schemas import ChatRequest, ChatResponse, Message, Role
from app.ai.models.base_models import AIConversation, AIMessage
import uuid

class CopilotService:
    """Main entry point for AI Chat interactions."""
    def __init__(self, db: Session):
        self.db = db
        self.repo = AIRepository(db)
        self.memory = MemoryManager(self.repo)
        self.context_builder = ContextBuilder(db)
        self.prompts = PromptTemplateService(self.repo)
        self.tools = ToolRegistry(db)
        
        # Hardcoded provider for now, would be injected or loaded from config
        self.llm_provider = MockLLMProvider()

    def process_chat(
        self, 
        request: ChatRequest, 
        org_id: str, 
        user_id: str
    ) -> ChatResponse:
        
        # 1. Fetch or Create Conversation
        if request.conversation_id:
            conv = self.repo.get_conversation(request.conversation_id, org_id)
            if not conv:
                raise ValueError("Conversation not found or unauthorized.")
        else:
            conv = self.repo.create_conversation(AIConversation(
                organization_id=org_id,
                user_id=user_id,
                agent_type=request.agent_type,
                title="New Chat"
            ))

        # 2. Add User Message
        user_msg = AIMessage(
            conversation_id=conv.id,
            sequence_number=len(self.repo.get_messages(conv.id)) + 1,
            role=Role.USER,
            content=request.message
        )
        self.repo.add_message(user_msg)

        # 3. Build Context
        context_str = self.context_builder.build_context(request.context_data or {}, org_id, user_id)
        
        # 4. Render System Prompt
        sys_prompt_content = self.prompts.render_prompt(
            f"{request.agent_type}_system", 
            org_id, 
            {"context": context_str}
        )

        # 5. Build Message History
        history = self.memory.get_conversation_history(conv.id)
        
        # Prepend System Prompt
        messages_for_llm = [Message(role=Role.SYSTEM, content=sys_prompt_content)] + history

        # 6. Execute Orchestrator
        # Could dynamically select based on agent_type
        agent = RecruiterCopilot(
            llm=self.llm_provider,
            tools=self.tools,
            prompts=self.prompts
        )
        
        ai_response_msg = agent.execute_loop(
            agent_type=request.agent_type,
            messages=messages_for_llm,
            org_id=org_id,
            user_id=user_id
        )

        # 7. Save Assistant Message
        assistant_db_msg = AIMessage(
            conversation_id=conv.id,
            sequence_number=user_msg.sequence_number + 10, # Leave room for tool calls if we wanted to save them
            role=Role.ASSISTANT,
            content=ai_response_msg.content,
            tool_calls=[t.dict() for t in ai_response_msg.tool_calls] if ai_response_msg.tool_calls else None
        )
        self.repo.add_message(assistant_db_msg)

        # 8. Return
        return ChatResponse(
            conversation_id=conv.id,
            message=ai_response_msg,
            trace_id=None # To be populated by ObservabilityService
        )

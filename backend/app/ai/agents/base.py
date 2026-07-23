from typing import Dict, Any, List
from app.ai.providers.base import LLMProvider
from app.ai.tools.registry import ToolRegistry
from app.ai.prompts.prompt_manager import PromptTemplateService
from app.ai.schemas.schemas import Message

class AgentOrchestrator:
    """Base orchestrator for executing multi-step AI reasoning loops."""
    def __init__(
        self,
        llm: LLMProvider,
        tools: ToolRegistry,
        prompts: PromptTemplateService,
    ):
        self.llm = llm
        self.tools = tools
        self.prompts = prompts
        self.max_steps = 5

    def execute_loop(
        self, 
        agent_type: str, 
        messages: List[Message], 
        org_id: str,
        user_id: str
    ) -> Message:
        """
        Executes a Tool-calling loop until the LLM returns a text response or hits max_steps.
        """
        step = 0
        current_messages = list(messages)
        
        while step < self.max_steps:
            # 1. Call LLM
            response = self.llm.chat(
                messages=current_messages,
                model="gpt-4", # Placeholder, would be configured per org/agent
                tools=self.tools.get_schemas()
            )
            
            ai_message_data = response["message"]
            ai_message = Message(**ai_message_data)
            current_messages.append(ai_message)

            # 2. Check if Tool Call requested
            if not ai_message.tool_calls:
                return ai_message # We have a final text response

            # 3. Execute Tools
            for tool_call in ai_message.tool_calls:
                tool_result = self.tools.execute_tool(
                    name=tool_call.name,
                    arguments_json=tool_call.arguments,
                    org_id=org_id,
                    user_id=user_id
                )
                
                # Append tool response
                tool_msg = Message(
                    role="tool",
                    content=tool_result,
                    tool_call_id=tool_call.id
                )
                current_messages.append(tool_msg)
                
            step += 1
            
        # Fallback if max steps reached
        return Message(
            role="assistant",
            content="I reached the maximum number of steps while trying to resolve your request."
        )

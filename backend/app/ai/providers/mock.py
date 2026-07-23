from typing import List, Dict, Any, Optional
import time
import json
from app.ai.providers.base import LLMProvider, EmbeddingProvider
from app.ai.schemas.schemas import Message, ToolSchema, Role

class MockLLMProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    def chat(
        self,
        messages: List[Message],
        model: str,
        tools: Optional[List[ToolSchema]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(0.1)

        last_message = messages[-1].content.lower() if messages[-1].content else ""
        
        # Determine behavior based on last message (a very dumb mock planner)
        tool_calls = None
        content = None
        
        if tools and "search" in last_message:
            # Simulate invoking a search tool
            tool_calls = [{
                "id": "call_mock_search_1",
                "name": "search_candidates",
                "arguments": json.dumps({"query": "software engineer"})
            }]
        elif messages[-1].role == Role.TOOL:
            # Answer based on tool output
            content = f"I found some information from the tool: {messages[-1].content}. Let me know if you need anything else."
        else:
            content = f"Mock response for: '{last_message[:50]}...'. I am a deterministic test provider."

        latency = (time.time() - start_time) * 1000
        
        return {
            "message": {
                "role": Role.ASSISTANT,
                "content": content,
                "tool_calls": tool_calls
            },
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            },
            "latency_ms": latency
        }

class MockEmbeddingProvider(EmbeddingProvider):
    @property
    def name(self) -> str:
        return "mock"

    def embed(
        self,
        text: str,
        model: str
    ) -> List[float]:
        # Return a simple deterministic embedding vector for tests
        return [0.1, 0.2, 0.3, 0.4, 0.5]

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.ai.schemas.schemas import Message, ToolSchema

class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Message],
        model: str,
        tools: Optional[List[ToolSchema]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to the LLM provider.
        Returns a dictionary containing the response message, token counts, and latency.
        """
        pass

class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def embed(
        self,
        text: str,
        model: str
    ) -> List[float]:
        """
        Generate embeddings for a given string.
        """
        pass

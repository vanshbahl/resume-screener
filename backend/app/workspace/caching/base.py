from abc import ABC, abstractmethod
from typing import Any, Optional

class CacheRepository(ABC):
    """
    Abstract interface for workspace caching.
    Allows for future Redis integration without changing service code.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
        
    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        pass
        
    @abstractmethod
    def delete(self, key: str) -> None:
        pass
        
    @abstractmethod
    def clear(self) -> None:
        pass

from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import threading
from .base import CacheRepository

class MemoryCacheRepository(CacheRepository):
    """
    In-memory caching implementation for rapid local execution.
    Thread-safe.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryCacheRepository, cls).__new__(cls)
                cls._instance.store: Dict[str, Dict[str, Any]] = {}
            return cls._instance

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self.store:
                return None
            
            item = self.store[key]
            if item["expires_at"] and datetime.utcnow() > item["expires_at"]:
                del self.store[key]
                return None
                
            return item["value"]
            
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = 300) -> None:
        with self._lock:
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
                
            self.store[key] = {
                "value": value,
                "expires_at": expires_at
            }
            
    def delete(self, key: str) -> None:
        with self._lock:
            if key in self.store:
                del self.store[key]
                
    def clear(self) -> None:
        with self._lock:
            self.store.clear()
            
# Global singleton instance for injection
memory_cache = MemoryCacheRepository()

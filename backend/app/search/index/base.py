from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class SearchIndex(ABC):
    """Base interface for all search indexes."""
    
    def __init__(self):
        self.metadata = {
            "index_version": "1.0",
            "build_timestamp": datetime.utcnow().isoformat(),
            "indexed_documents": 0
        }
    
    @abstractmethod
    def index_document(self, doc_id: str, payload: Any):
        """Indexes a document payload."""
        pass
        
    @abstractmethod
    def remove_document(self, doc_id: str):
        """Removes a document from the index."""
        pass
        
    @abstractmethod
    def clear(self):
        """Clears all data from the index."""
        pass
        
    @abstractmethod
    def get_document(self, doc_id: str) -> Any:
        """Retrieves a document by ID."""
        pass

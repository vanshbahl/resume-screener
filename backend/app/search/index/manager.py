from typing import Dict, Any
from app.search.index.base import SearchIndex
from app.search.index.candidate import CandidateIndex
from app.search.index.job import JobIndex

class IndexManager:
    """Orchestrates index lifecycle, startup loading, and cache invalidation."""
    
    def __init__(self):
        self.indexes: Dict[str, SearchIndex] = {
            "candidate": CandidateIndex(),
            "job": JobIndex()
        }
        
    def get_index(self, index_name: str) -> SearchIndex:
        if index_name not in self.indexes:
            raise ValueError(f"Index '{index_name}' not found.")
        return self.indexes[index_name]
        
    def rebuild_index(self, index_name: str, documents: Dict[str, Any]):
        """Clears and rebuilds an index from scratch."""
        index = self.get_index(index_name)
        index.clear()
        for doc_id, payload in documents.items():
            index.index_document(doc_id, payload)
            
    def get_metadata(self) -> Dict[str, Any]:
        """Exposes metadata for all managed indexes."""
        return {name: idx.metadata for name, idx in self.indexes.items()}

# Singleton instance
index_manager = IndexManager()

from typing import Dict, Any, List, Set
from app.search.index.base import SearchIndex
from app.schemas.intelligence import FeatureVector

class CandidateIndex(SearchIndex):
    """In-memory inverted index for Candidate FeatureVectors."""
    
    def __init__(self):
        super().__init__()
        self.documents: Dict[str, FeatureVector] = {}
        
        # Inverted indexes for O(1) lookups
        self.skill_index: Dict[str, Set[str]] = {}
        self.location_index: Dict[str, Set[str]] = {}
        
    def index_document(self, doc_id: str, payload: FeatureVector):
        self.documents[doc_id] = payload
        
        # Build inverted skills index
        for skill in payload.skills + payload.frameworks + payload.tools:
            canon = skill.lower()
            if canon not in self.skill_index:
                self.skill_index[canon] = set()
            self.skill_index[canon].add(doc_id)
            
        self.metadata["indexed_documents"] = len(self.documents)
        self.metadata["build_timestamp"] = __import__('datetime').datetime.utcnow().isoformat()

    def remove_document(self, doc_id: str):
        if doc_id in self.documents:
            payload = self.documents.pop(doc_id)
            
            # Clean up inverted indexes
            for skill in payload.skills + payload.frameworks + payload.tools:
                canon = skill.lower()
                if canon in self.skill_index:
                    self.skill_index[canon].discard(doc_id)
                    if not self.skill_index[canon]:
                        del self.skill_index[canon]
            
            self.metadata["indexed_documents"] = len(self.documents)

    def clear(self):
        self.documents.clear()
        self.skill_index.clear()
        self.location_index.clear()
        self.metadata["indexed_documents"] = 0
        
    def get_document(self, doc_id: str) -> FeatureVector:
        return self.documents.get(doc_id)
        
    def find_by_skill(self, skill: str) -> Set[str]:
        return self.skill_index.get(skill.lower(), set())

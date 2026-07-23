from typing import Dict, Set

from app.schemas.intelligence import FeatureVector
from app.search.index.base import SearchIndex


class JobIndex(SearchIndex):
    """In-memory inverted index for Job FeatureVectors."""

    def __init__(self):
        super().__init__()
        self.documents: Dict[str, FeatureVector] = {}

        # Inverted indexes for O(1) lookups
        self.skill_index: Dict[str, Set[str]] = {}

    def index_document(self, doc_id: str, payload: FeatureVector):
        self.documents[doc_id] = payload

        for skill in payload.skills + payload.frameworks + payload.tools:
            canon = skill.lower()
            if canon not in self.skill_index:
                self.skill_index[canon] = set()
            self.skill_index[canon].add(doc_id)

        self.metadata["indexed_documents"] = len(self.documents)

    def remove_document(self, doc_id: str):
        if doc_id in self.documents:
            payload = self.documents.pop(doc_id)
            for skill in payload.skills + payload.frameworks + payload.tools:
                canon = skill.lower()
                if canon in self.skill_index:
                    self.skill_index[canon].discard(doc_id)
            self.metadata["indexed_documents"] = len(self.documents)

    def clear(self):
        self.documents.clear()
        self.skill_index.clear()
        self.metadata["indexed_documents"] = 0

    def get_document(self, doc_id: str) -> FeatureVector:
        return self.documents.get(doc_id)

import pytest
from app.search.index.manager import index_manager
from app.schemas.intelligence import FeatureVector

def test_index_manager_lifecycle():
    cand_idx = index_manager.get_index("candidate")
    cand_idx.clear()
    
    assert cand_idx.metadata["indexed_documents"] == 0
    
    vec = FeatureVector(skills=["Python", "Java"])
    cand_idx.index_document("c1", vec)
    
    assert cand_idx.metadata["indexed_documents"] == 1
    assert "c1" in cand_idx.find_by_skill("Python")
    
    cand_idx.remove_document("c1")
    assert cand_idx.metadata["indexed_documents"] == 0
    assert "c1" not in cand_idx.find_by_skill("Python")

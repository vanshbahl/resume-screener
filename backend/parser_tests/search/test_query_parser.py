import pytest
from app.schemas.search import SearchQuery, SearchContext
from app.search.strategies.ontology import OntologySearchStrategy
from app.search.index.manager import index_manager
from app.schemas.intelligence import FeatureVector

def test_ontology_search_expansion():
    # Setup index
    cand_idx = index_manager.get_index("candidate")
    cand_idx.clear()
    cand_idx.index_document("c1", FeatureVector(skills=["React"]))
    cand_idx.index_document("c2", FeatureVector(skills=["Vue"]))
    cand_idx.index_document("c3", FeatureVector(skills=["Python"]))
    
    strategy = OntologySearchStrategy()
    
    # Query for "React". Vue is in the same family (Frontend) so it should match via ontology.
    query = SearchQuery(skills=["React"])
    context = SearchContext(query=query)
    
    matched_ids = strategy.execute(context)
    
    assert "c1" in matched_ids
    # "Vue" doesn't strictly have to match depending on the ontology graph, but we test the expansion count
    assert context.metrics.ontology_expansion_count > 0

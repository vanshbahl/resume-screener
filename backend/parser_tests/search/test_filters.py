import pytest
from app.search.filter_engine import filter_engine
from app.schemas.search import SearchQuery, SearchContext, NumberRange
from app.schemas.intelligence import FeatureVector
from app.search.index.manager import index_manager

def test_filter_engine_experience():
    cand_idx = index_manager.get_index("candidate")
    cand_idx.clear()
    
    cand_idx.index_document("c1", FeatureVector(years_experience=2.0))
    cand_idx.index_document("c2", FeatureVector(years_experience=5.0))
    
    query = SearchQuery(experience=NumberRange(min=3.0, max=10.0))
    context = SearchContext(query=query)
    
    filtered_ids = filter_engine.apply_filters(context, {"c1", "c2"})
    
    assert "c2" in filtered_ids
    assert "c1" not in filtered_ids
    assert context.metrics.filter_drop_rate == 0.5

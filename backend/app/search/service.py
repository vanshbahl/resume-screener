from app.schemas.search import SearchContext, SearchQuery, SearchResponse
from app.search.strategies.keyword import KeywordSearchStrategy
from app.search.strategies.ontology import OntologySearchStrategy
from app.search.filter_engine import filter_engine
from app.search.ranking_adapter import ranking_adapter
from app.search.result_formatter import result_formatter

class SearchService:
    """Orchestrates the entire search pipeline."""
    
    def __init__(self):
        self.strategies = {
            "keyword": KeywordSearchStrategy(),
            "ontology": OntologySearchStrategy(),
            "hybrid": OntologySearchStrategy() # Default hybrid to ontology for now
        }
        
    def execute_search(self, query: SearchQuery, target_type: str = "candidate") -> SearchResponse:
        context = SearchContext(query=query, target_type=target_type)
        context.start_timer()
        
        # 1. Retrieval
        strategy = self.strategies.get(query.search_type, self.strategies["hybrid"])
        raw_ids = strategy.execute(context)
        context.metrics.candidate_count_initial = len(raw_ids)
        
        # 2. Filtering
        filtered_ids = filter_engine.apply_filters(context, raw_ids)
        
        # 3. Ranking
        ranked_items = ranking_adapter.rank_results(context, filtered_ids)
        
        # 4. Formatting
        results = result_formatter.format_results(context, ranked_items)
        
        context.end_timer()
        
        return SearchResponse(
            results=results,
            total_found=len(results),
            context=context
        )

# Singleton instance
search_service = SearchService()

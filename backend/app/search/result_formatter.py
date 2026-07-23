from typing import List, Dict, Any
from app.schemas.search import SearchContext, SearchResult

class ResultFormatter:
    """Formats ranked results into standard SearchResult models."""
    
    def format_results(self, context: SearchContext, ranked_items: List[Dict[str, Any]]) -> List[SearchResult]:
        results = []
        for item in ranked_items:
            # Generate highlights (simple intersection for now)
            highlights = {"skills": item["doc"].skills[:3]}
            
            # Pull expansions used
            expansions = []
            for k, v in context.expanded_terms.items():
                if set(v).intersection(set(item["doc"].skills)):
                    expansions.append(k)
                    
            res = SearchResult(
                target_id=item["target_id"],
                target_type=context.target_type,
                match_score=item["score"], # Can separate later
                ranking_score=item["score"],
                highlighted_fields=highlights,
                matched_entities=list(set(context.query.skills).intersection(set(item["doc"].skills))),
                ontology_expansions_used=expansions,
                confidence=1.0,
                explanations=item["explanations"]
            )
            results.append(res)
        return results

# Singleton instance
result_formatter = ResultFormatter()

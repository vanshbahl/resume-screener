from typing import Set, Dict, Any
from app.schemas.search import SearchContext
from app.search.index.manager import index_manager

class FilterEngine:
    """Applies hard constraints to a set of candidate IDs."""
    
    def apply_filters(self, context: SearchContext, candidate_ids: Set[str]) -> Set[str]:
        index = index_manager.get_index(context.target_type)
        filtered_ids = set()
        
        initial_count = len(candidate_ids)
        
        for doc_id in candidate_ids:
            doc = index.get_document(doc_id)
            if not doc:
                continue
                
            passed = True
            
            # Apply Experience bounds
            if context.query.experience:
                if context.query.experience.min is not None:
                    if getattr(doc, "years_experience", 0.0) < context.query.experience.min:
                        passed = False
                if context.query.experience.max is not None:
                    if getattr(doc, "years_experience", 0.0) > context.query.experience.max:
                        passed = False
                        
            # Apply Education bounds
            if context.query.education_levels and passed:
                if getattr(doc, "education_level", "none") not in context.query.education_levels:
                    passed = False
                    
            if passed:
                filtered_ids.add(doc_id)
                
        final_count = len(filtered_ids)
        context.metrics.candidate_count_filtered = final_count
        if initial_count > 0:
            context.metrics.filter_drop_rate = (initial_count - final_count) / initial_count
            
        return filtered_ids

# Singleton instance
filter_engine = FilterEngine()

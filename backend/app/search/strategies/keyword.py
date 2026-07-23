from typing import Set

from app.schemas.search import SearchContext
from app.search.strategies.base import SearchStrategy


class KeywordSearchStrategy(SearchStrategy):
    """Executes exact keyword intersection search."""

    def execute(self, context: SearchContext) -> Set[str]:
        index = self.index_manager.get_index(context.target_type)

        # If it's a CandidateIndex, we can use find_by_skill
        if not hasattr(index, "find_by_skill"):
            # Fallback for generic text scanning
            return self._fallback_scan(index, context)

        matched_ids = set()

        # We look for all queried skills
        for skill in context.query.skills:
            ids = index.find_by_skill(skill)
            if not matched_ids:
                matched_ids.update(ids)
            else:
                # Intersection for strict keyword matching (AND behavior)
                matched_ids.intersection_update(ids)

            context.metrics.ontology_expansion_count += 0  # No ontology used

        return matched_ids

    def _fallback_scan(self, index, context: SearchContext) -> Set[str]:
        # Brute force scan over documents (inefficient, fallback only)
        matched_ids = set()
        for doc_id, doc in index.documents.items():
            # Example basic check
            matched = True
            for skill in context.query.skills:
                if skill not in getattr(doc, "skills", []):
                    matched = False
                    break
            if matched:
                matched_ids.add(doc_id)
        return matched_ids

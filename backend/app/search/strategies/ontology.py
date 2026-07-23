from typing import Set

from app.intelligence.ontology_service import ontology_service
from app.schemas.search import SearchContext
from app.search.strategies.base import SearchStrategy


class OntologySearchStrategy(SearchStrategy):
    """Executes search with Ontology expansion (OR-expansion of siblings/aliases)."""

    def execute(self, context: SearchContext) -> Set[str]:
        index = self.index_manager.get_index(context.target_type)
        if not hasattr(index, "find_by_skill"):
            return set()

        matched_ids = set()

        for skill in context.query.skills:
            # 1. Expand skill
            canon = ontology_service.get_canonical_name(skill)
            related = ontology_service.get_related(canon)

            expansions = [canon] + related
            context.expanded_terms[skill] = expansions
            context.metrics.ontology_expansion_count += len(related)

            # 2. Find any doc matching ANY of the expansions (OR behavior within the skill cluster)
            cluster_matched = set()
            for exp in expansions:
                cluster_matched.update(index.find_by_skill(exp))

            # 3. Intersect across different queried skills (AND behavior across clusters)
            if not matched_ids:
                matched_ids.update(cluster_matched)
            else:
                matched_ids.intersection_update(cluster_matched)

        return matched_ids

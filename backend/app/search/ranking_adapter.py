import time
from typing import Any, Dict, List, Set

from app.intelligence.scoring_service import scoring_service
from app.schemas.intelligence import Explanation, FeatureVector, MatchResult
from app.schemas.search import SearchContext
from app.search.index.manager import index_manager


class RankingAdapter:
    """Bridges search results with the existing ScoringService."""

    def rank_results(
        self, context: SearchContext, filtered_ids: Set[str]
    ) -> List[Dict[str, Any]]:
        start_time = time.time()
        index = index_manager.get_index(context.target_type)

        # We need to create a synthetic Job FeatureVector from the SearchQuery
        # to feed into the ScoringService (which expects MatchResults)
        req_vec = FeatureVector(
            skills=context.query.skills,
            frameworks=context.query.frameworks,
            years_experience=(
                context.query.experience.min if context.query.experience else 0.0
            ),
        )

        ranked_items = []
        for doc_id in filtered_ids:
            doc = index.get_document(doc_id)

            # 1. Generate Synthetic MatchResult
            # In a real app we'd use MatchingService.match here, but we can shortcut
            # for search performance.
            explanations = [
                Explanation(
                    category="search",
                    matched_entities=list(set(doc.skills).intersection(req_vec.skills)),
                    missing_entities=[],
                    confidence=1.0,
                    reason="Matched from search index.",
                    evidence="Retrieved via index lookup",
                )
            ]

            match_res = MatchResult(
                candidate_id=doc_id,
                job_id="search_query",
                matched_features=doc,
                missing_features_required=FeatureVector(),
                missing_features_preferred=FeatureVector(),
                explanations=explanations,
            )

            # 2. Score it
            score_res = scoring_service.score_match(match_res)

            ranked_items.append(
                {
                    "target_id": doc_id,
                    "doc": doc,
                    "score": score_res.overall_score,
                    "explanations": score_res.explanations,
                }
            )

        # 3. Sort
        ranked_items.sort(key=lambda x: x["score"], reverse=True)

        context.metrics.ranking_time_ms = (time.time() - start_time) * 1000
        return ranked_items


# Singleton instance
ranking_adapter = RankingAdapter()

from typing import List, Dict
from app.schemas.intelligence import ScoreResult, RankingResult, RankedItem

class RankingService:
    def rank_candidates_for_job(self, job_id: str, score_results: List[ScoreResult]) -> RankingResult:
        """Ranks a list of ScoreResults for a specific job."""
        
        # Sort by overall score descending
        sorted_scores = sorted(score_results, key=lambda x: x.overall_score, reverse=True)
        
        rankings = []
        for i, score_res in enumerate(sorted_scores):
            # Generate deterministic reason
            reason = f"Rank {i+1} with score {score_res.overall_score}%."
            if score_res.overall_score > 80:
                reason += " Exceptional alignment."
            elif score_res.overall_score < 50:
                reason += " Fails to meet minimum thresholds."
                
            rankings.append(RankedItem(
                target_id=score_res.candidate_id,
                score=score_res.overall_score,
                reason=reason
            ))
            
        return RankingResult(
            ranking_context=f"Candidates for Job {job_id}",
            rankings=rankings
        )
        
    def rank_generic(self, items: List[Dict[str, float]], context: str) -> RankingResult:
        """
        Generic ranking for arbitrary items containing a target_id and a score.
        Example item: {"target_id": "proj_123", "score": 95.5}
        """
        sorted_items = sorted(items, key=lambda x: x.get("score", 0.0), reverse=True)
        
        rankings = []
        for i, item in enumerate(sorted_items):
            score = item.get("score", 0.0)
            rankings.append(RankedItem(
                target_id=item.get("target_id", "unknown"),
                score=score,
                reason=f"Rank {i+1} based on score."
            ))
            
        return RankingResult(
            ranking_context=context,
            rankings=rankings
        )

# Singleton instance
ranking_service = RankingService()

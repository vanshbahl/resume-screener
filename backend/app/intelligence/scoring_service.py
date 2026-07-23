from typing import Dict
from app.schemas.intelligence import MatchResult, ScoreResult, Explanation
from app.parsers.core.config_loader import load_config

class ScoringService:
    def __init__(self):
        # Load weights on init
        raw_config = load_config("matching_weights.yaml")
        if isinstance(raw_config, dict):
            self.weights = raw_config.get("weights", {})
        else:
            self.weights = {
                'technical_skills': 0.30,
                'experience': 0.25,
                'projects': 0.15,
                'education': 0.10,
                'responsibilities': 0.10,
                'soft_skills': 0.05,
                'other': 0.05
            }

    def score_match(self, match_result: MatchResult) -> ScoreResult:
        """Computes deterministic 0-100 score from MatchResult explanations."""
        category_scores: Dict[str, float] = {}
        total_score = 0.0
        
        # 1. Score Technical Skills (skills, frameworks, tools, concepts, databases, cloud, languages)
        tech_matched = 0
        tech_total = 0
        
        # 2. Score Soft Skills
        soft_matched = 0
        soft_total = 0
        
        for exp in match_result.explanations:
            # Experience handled separately below
            if exp.category == "experience":
                continue
                
            total_req = len(exp.matched_entities) + len(exp.missing_entities)
            
            if exp.category == "soft_skills":
                soft_total += total_req
                soft_matched += len(exp.matched_entities)
            else:
                tech_total += total_req
                tech_matched += len(exp.matched_entities)
                
            # Update explanation contribution retroactively for traceability
            if total_req > 0:
                exp.weighted_contribution = len(exp.matched_entities) / total_req
                
        # 3. Compute Category Percentages (0 - 100)
        tech_score = (tech_matched / tech_total * 100) if tech_total > 0 else 100.0
        soft_score = (soft_matched / soft_total * 100) if soft_total > 0 else 100.0
        
        # 4. Score Experience
        exp_score = 100.0
        for exp in match_result.explanations:
            if exp.category == "experience":
                if exp.missing_entities:
                    # Partial score for missing experience
                    # E.g. Missing 2 years out of 5 -> 3/5 = 60%
                    missing_yoe = float(exp.missing_entities[0])
                    matched_yoe = float(exp.matched_entities[0]) if exp.matched_entities else 0.0
                    if missing_yoe > 0:
                        exp_score = min(100.0, max(0.0, (matched_yoe / missing_yoe) * 100))
                exp.weighted_contribution = exp_score / 100.0

        # Assemble category scores
        category_scores["technical_skills"] = tech_score
        category_scores["experience"] = exp_score
        category_scores["soft_skills"] = soft_score
        category_scores["projects"] = 100.0 # Placeholder: Would calculate from project complexity
        category_scores["education"] = 100.0 # Placeholder: Would calculate from education level reqs
        
        # 5. Apply Configured Weights
        for cat, val in category_scores.items():
            weight = self.weights.get(cat, 0.0)
            total_score += val * weight
            
        # Ensure we cap at 100
        overall_score = min(100.0, round(total_score, 2))
        
        return ScoreResult(
            candidate_id=match_result.candidate_id,
            job_id=match_result.job_id,
            overall_score=overall_score,
            category_scores=category_scores,
            explanations=match_result.explanations
        )

# Singleton instance
scoring_service = ScoringService()

from typing import List
from app.schemas.decision import LearningRecommendation, CareerRecommendation, HiringRecommendation, OpportunityRecommendation, RiskReport
from app.schemas.intelligence import GapAnalysis, CandidateProfile, ScoreResult
from app.parsers.core.config_loader import load_config
from app.intelligence.ontology_service import ontology_service
from app.intelligence.insight_service import insight_service

class LearningRecommendationService:
    def __init__(self):
        config = load_config("recommendation/learning_paths.yaml")
        self.paths = config.get("paths", {}) if isinstance(config, dict) else {}
        
    def generate_recommendations(self, gap_analysis: GapAnalysis) -> List[LearningRecommendation]:
        recs = []
        for skill in gap_analysis.missing_critical_skills:
            path = self.paths.get(skill)
            family = ontology_service.get_semantic_family(skill)
            
            recs.append(LearningRecommendation(
                action=f"Learn {skill}",
                reason="Critical required skill missing.",
                evidence=f"Required by Job {gap_analysis.job_id}",
                estimated_score_improvement=10.0,
                priority="high",
                estimated_difficulty="medium",
                skill_target=skill,
                learning_path=path or f"Explore {family} domain courses."
            ))
        return recs

class CareerRecommendationService:
    def generate_recommendations(self, candidate: CandidateProfile) -> List[CareerRecommendation]:
        recs = []
        insights = insight_service.generate_insights(candidate.vector)
        
        has_leadership = any(i.title == "Leadership Potential" for i in insights)
        
        if has_leadership:
            recs.append(CareerRecommendation(
                action="Target Senior/Lead Roles",
                reason="Strong combination of tenure and leadership indicators.",
                evidence=f"{candidate.vector.years_experience} YOE with leadership markers.",
                estimated_score_improvement=0.0, # N/A for self-guided career recs
                priority="medium",
                suggested_role="Tech Lead / Engineering Manager",
                transferable_skills=["Management", "Architecture"]
            ))
            
        if candidate.vector.technology_focus == "specialist":
            recs.append(CareerRecommendation(
                action="Deepen Niche Expertise",
                reason="Profile indicates deep specialization.",
                evidence="Technology pool is narrow and deep.",
                suggested_role="Domain Expert / Staff Engineer",
                transferable_skills=candidate.vector.skills[:3]
            ))
            
        return recs

class HiringRecommendationService:
    def __init__(self):
        config = load_config("recommendation/recommendation_rules.yaml")
        self.rules = config.get("hiring_categories", {}) if isinstance(config, dict) else {}
        
    def categorize_candidate(self, score_res: ScoreResult, risk: RiskReport) -> HiringRecommendation:
        top = self.rules.get("top_candidate", {"min_score": 80.0})
        gem = self.rules.get("hidden_gem", {"min_score": 55.0, "required_insight": "Leadership Potential"})
        
        category = "needs_review"
        reason = "Did not meet strict categorization thresholds."
        
        # We can implement full logic, simplified for deterministic engine here
        if score_res.overall_score >= top.get("min_score", 80.0) and risk.overall_risk_level in ["low", "medium"]:
            category = "top_candidate"
            reason = "High match score with acceptable risk."
        elif risk.overall_risk_level in ["high", "critical"]:
            category = "high_risk"
            reason = "Critical or High risk factors detected."
        elif score_res.overall_score >= gem.get("min_score", 55.0) and risk.overall_risk_level == "low":
            category = "hidden_gem"
            reason = "Lower match score but strong fundamentals and low risk."
            
        return HiringRecommendation(
            action=f"Mark as {category}",
            reason=reason,
            evidence=f"Score: {score_res.overall_score}%, Risk: {risk.overall_risk_level}",
            candidate_category=category,
            job_id=score_res.job_id,
            match_score=score_res.overall_score
        )

# Singleton instances
learning_recommender = LearningRecommendationService()
career_recommender = CareerRecommendationService()
hiring_recommender = HiringRecommendationService()

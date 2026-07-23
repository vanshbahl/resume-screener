from typing import List
from app.schemas.intelligence import GapAnalysis, Recommendation
from app.intelligence.ontology_service import ontology_service

class RecommendationService:
    def generate_recommendations(self, gap_analysis: GapAnalysis) -> List[Recommendation]:
        """Generates deterministic recommendations to close gaps based on the gap analysis."""
        recommendations = []
        
        # Skill Recommendations
        for skill in gap_analysis.missing_critical_skills:
            family = ontology_service.get_semantic_family(skill)
            action = f"Learn and build a project using {skill}"
            reason = f"Critical required skill missing from profile."
            if family:
                action += f" (Domain: {family})"
                
            recommendations.append(Recommendation(
                gap_type="critical_skill",
                action=action,
                estimated_score_improvement=5.0, # Heuristic static estimate
                reason=reason
            ))
            
        for skill in gap_analysis.missing_preferred_skills:
            recommendations.append(Recommendation(
                gap_type="preferred_skill",
                action=f"Consider exploring {skill} to stand out.",
                estimated_score_improvement=2.0,
                reason="Preferred skill missing, would increase competitiveness."
            ))
            
        # Experience Recommendations
        if gap_analysis.experience_gap_years > 0:
            recommendations.append(Recommendation(
                gap_type="experience",
                action=f"Gain {gap_analysis.experience_gap_years} more years of relevant experience.",
                estimated_score_improvement=15.0,
                reason="Current tenure falls short of the required baseline."
            ))
            
        # Education Recommendations
        if gap_analysis.education_gap:
            recommendations.append(Recommendation(
                gap_type="education",
                action="Consider pursuing the required degree level or obtaining equivalent high-tier certifications.",
                estimated_score_improvement=10.0,
                reason="Formal education level is below the minimum job requirement."
            ))
            
        return recommendations

# Singleton instance
recommendation_service = RecommendationService()

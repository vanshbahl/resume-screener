from typing import List
from app.schemas.intelligence import FeatureVector, Insight

class InsightService:
    def generate_insights(self, candidate_vec: FeatureVector) -> List[Insight]:
        """Analyzes a single Candidate Profile to generate heuristic insights."""
        insights = []
        
        # Total skills metric
        total_tech_skills = len(candidate_vec.skills) + len(candidate_vec.frameworks) + len(candidate_vec.tools) + len(candidate_vec.languages) + len(candidate_vec.databases) + len(candidate_vec.cloud)
        
        if total_tech_skills > 15:
            insights.append(Insight(
                title="Strong Skill Breadth",
                description="Candidate possesses a wide variety of technical competencies across multiple domains.",
                category="Strength",
                evidence=f"Extracted {total_tech_skills} total technical skills."
            ))
            
        if candidate_vec.years_experience > 5.0 and candidate_vec.leadership_score > 0.0:
            insights.append(Insight(
                title="Leadership Potential",
                description="Candidate shows signs of technical leadership experience combined with tenure.",
                category="Strength",
                evidence=f"Has {candidate_vec.years_experience} YOE and leadership keywords detected."
            ))
            
        if candidate_vec.technology_focus == "specialist":
            insights.append(Insight(
                title="Deep Technology Focus",
                description="Candidate is highly focused on a smaller, niche set of technologies.",
                category="Observation",
                evidence="Technology pool is narrow and specialized."
            ))
            
        if candidate_vec.project_complexity_score > 2.0:
            insights.append(Insight(
                title="High Project Volume",
                description="Candidate has built and showcased multiple projects.",
                category="Strength",
                evidence=f"Complexity score: {candidate_vec.project_complexity_score} based on project array."
            ))
            
        return insights

# Singleton instance
insight_service = InsightService()

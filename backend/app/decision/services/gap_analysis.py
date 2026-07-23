from app.schemas.intelligence import FeatureVector, GapAnalysis
from app.intelligence.ontology_service import ontology_service

class GapAnalysisService:
    def analyze_gap(self, candidate_id: str, job_id: str, candidate_vec: FeatureVector, req_vec: FeatureVector, pref_vec: FeatureVector = None) -> GapAnalysis:
        """Upgraded deterministic Gap Report supporting leadership and soft skill gaps."""
        
        missing_critical = []
        for cat in ["skills", "frameworks", "tools", "concepts", "languages", "databases", "cloud", "soft_skills"]:
            req_items = set(getattr(req_vec, cat, []))
            cand_items = set(getattr(candidate_vec, cat, []))
            
            # Ontology check: if we require X, do we have something in the same family?
            missing = req_items.difference(cand_items)
            for m in list(missing):
                resolved = False
                m_family = ontology_service.get_semantic_family(m)
                if m_family:
                    for c in cand_items:
                        if ontology_service.get_semantic_family(c) == m_family:
                            resolved = True
                            break
                if not resolved:
                    missing_critical.append(m)
            
        missing_pref = []
        if pref_vec:
            for cat in ["skills", "frameworks", "tools", "concepts", "languages", "databases", "cloud", "soft_skills"]:
                pref_items = set(getattr(pref_vec, cat, []))
                cand_items = set(getattr(candidate_vec, cat, []))
                missing = pref_items.difference(cand_items)
                missing_pref.extend(list(missing))
                
        experience_gap = max(0.0, req_vec.years_experience - candidate_vec.years_experience)
        
        # Education gap calculation
        ed_levels = {"none": 0, "high_school": 1, "bachelors": 2, "masters": 3, "phd": 4}
        cand_ed = ed_levels.get(candidate_vec.education_level, 0)
        req_ed = ed_levels.get(req_vec.education_level, 0)
        education_gap = cand_ed < req_ed

        return GapAnalysis(
            candidate_id=candidate_id,
            job_id=job_id,
            missing_critical_skills=missing_critical,
            missing_preferred_skills=missing_pref,
            experience_gap_years=experience_gap,
            education_gap=education_gap
        )

# Singleton instance
gap_analysis_service = GapAnalysisService()

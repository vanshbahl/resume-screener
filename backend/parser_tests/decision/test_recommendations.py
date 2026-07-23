import pytest
from app.schemas.intelligence import GapAnalysis, CandidateProfile, FeatureVector
from app.decision.services.recommendations import learning_recommender, career_recommender

def test_learning_recommender():
    gap = GapAnalysis(
        candidate_id="c1", job_id="j1",
        missing_critical_skills=["AWS", "React"],
        missing_preferred_skills=[],
        experience_gap_years=0.0,
        education_gap=False
    )
    
    recs = learning_recommender.generate_recommendations(gap)
    
    assert len(recs) == 2
    aws_rec = next(r for r in recs if r.skill_target == "AWS")
    # In learning_paths.yaml we set AWS to "AWS Certified Solutions Architect"
    assert "Solutions Architect" in aws_rec.learning_path

def test_career_recommender_specialist():
    # A candidate with few skills triggers specialist
    cand_vec = FeatureVector(skills=["Java", "Spring"], technology_focus="specialist")
    cand = CandidateProfile(candidate_id="c1", raw_text="", raw_data={}, vector=cand_vec)
    
    recs = career_recommender.generate_recommendations(cand)
    assert any("specialization" in r.reason.lower() or "expert" in r.suggested_role.lower() for r in recs)

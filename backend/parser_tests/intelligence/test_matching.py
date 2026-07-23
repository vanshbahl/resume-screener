import pytest
from app.schemas.intelligence import FeatureVector
from app.intelligence.matching_service import MatchingService
from app.intelligence.scoring_service import ScoringService

def test_match_and_score():
    matching_service = MatchingService()
    scoring_service = ScoringService()
    
    cand = FeatureVector(
        skills=["Python", "Java"],
        frameworks=["React"],
        years_experience=3.0,
        education_level="bachelors"
    )
    
    req = FeatureVector(
        skills=["Python", "JavaScript"],
        frameworks=["Vue"],
        years_experience=5.0,
        education_level="bachelors"
    )
    
    match_res = matching_service.match("c1", "j1", cand, req, FeatureVector())
    
    # Explanation checks
    assert len(match_res.explanations) > 0
    skills_exp = next(e for e in match_res.explanations if e.category == "skills")
    
    assert "Python" in skills_exp.matched_entities
    assert "JavaScript" in skills_exp.missing_entities
    
    score_res = scoring_service.score_match(match_res)
    
    # Overall score should be computed
    assert 0.0 <= score_res.overall_score <= 100.0
    
    # Since experience is 3 / 5, score should be 60 for experience
    assert score_res.category_scores["experience"] == 60.0


from app.decision.services.core_engines import risk_analysis_service
from app.schemas.intelligence import (CandidateProfile, FeatureVector,
                                      JobProfile)


def test_risk_analysis_overqualification():
    cand_vec = FeatureVector(years_experience=15.0, skills=[])
    cand = CandidateProfile(
        candidate_id="c1", raw_text="", raw_data={}, vector=cand_vec
    )

    job_vec = FeatureVector(years_experience=2.0, skills=[])
    job = JobProfile(
        job_id="j1",
        raw_text="",
        raw_data={},
        required_vector=job_vec,
        preferred_vector=FeatureVector(),
    )

    report = risk_analysis_service.analyze_risks(cand, job)

    assert report.overall_risk_level in ["low", "medium", "high", "critical"]
    assert any(r.risk_type == "overqualified" for r in report.risks)


def test_risk_analysis_skill_mismatch():
    cand_vec = FeatureVector(years_experience=3.0, skills=["Java"])
    cand = CandidateProfile(
        candidate_id="c1", raw_text="", raw_data={}, vector=cand_vec
    )

    # 4 skills required, candidate has 0 match
    job_vec = FeatureVector(
        years_experience=2.0, skills=["Python", "AWS", "Docker", "React"]
    )
    job = JobProfile(
        job_id="j1",
        raw_text="",
        raw_data={},
        required_vector=job_vec,
        preferred_vector=FeatureVector(),
    )

    report = risk_analysis_service.analyze_risks(cand, job)

    assert any(r.risk_type == "skill_mismatch" for r in report.risks)

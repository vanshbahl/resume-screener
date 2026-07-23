import os
import sys

from app.intelligence.feature_vector_service import feature_vector_service
from app.intelligence.matching_service import matching_service
from app.intelligence.scoring_service import scoring_service
from app.decision.services.gap_analysis import gap_analysis_service
from app.decision.services.recommendations import learning_recommender, career_recommender, hiring_recommender
from app.decision.services.core_engines import risk_analysis_service, decision_engine
from app.search.index.manager import index_manager
from app.schemas.search import SearchQuery, NumberRange
from app.api.search import search_candidates

def run_e2e():
    print("Starting E2E Validation...")
    
    # 1. Parse Resume
    print("1. Parsing Resume... (Mocked)")
    resume_path = "parser_tests/datasets/benchmark_v1/resumes/pdf/001_software_engineer.pdf"
    if not os.path.exists(resume_path):
        print(f"Skipping resume parsing, mock file not found: {resume_path}")
        # Create a mock CandidateProfile and JobProfile for the rest of the flow
        from app.schemas.intelligence import CandidateProfile, JobProfile, FeatureVector
        cand_vec = FeatureVector(years_experience=3.0, skills=["Python", "AWS", "React"], education_level="bachelors")
        cand_profile = CandidateProfile(candidate_id="c1", raw_text="mock", raw_data={}, vector=cand_vec)
        
        job_vec = FeatureVector(years_experience=2.0, skills=["Python", "AWS"], education_level="bachelors")
        job_profile = JobProfile(job_id="j1", raw_text="mock", raw_data={}, required_vector=job_vec, preferred_vector=FeatureVector())
    else:
        # We would parse here, but assume we mock for the sake of the E2E logical test
        pass

    # 2. Matching & Scoring
    print("2. Matching & Scoring...")
    match_res = matching_service.match(cand_profile.candidate_id, job_profile.job_id, cand_profile.vector, job_profile.required_vector, job_profile.preferred_vector)
    score_res = scoring_service.score_match(match_res)
    print(f"   Score: {score_res.overall_score}%")
    
    # 3. Gap Analysis
    print("3. Gap Analysis...")
    gap_res = gap_analysis_service.analyze_gap(cand_profile.candidate_id, job_profile.job_id, cand_profile.vector, job_profile.required_vector, job_profile.preferred_vector)
    print(f"   Gaps: Critical={len(gap_res.missing_critical_skills)}")
    
    # 4. Recommendations & Decisions
    print("4. Decisions...")
    risk_res = risk_analysis_service.analyze_risks(cand_profile, job_profile)
    decision = decision_engine.make_decision(score_res, risk_res)
    print(f"   Decision: {decision.decision}")
    
    # 5. Search
    print("5. Search...")
    idx = index_manager.get_index("candidate")
    idx.index_document(cand_profile.candidate_id, cand_profile.vector)
    
    query = SearchQuery(skills=["Python"], experience=NumberRange(min=1.0, max=5.0))
    # Direct service call to avoid FastAPI Request object needs
    from app.search.service import search_service
    search_res = search_service.execute_search(query, target_type="candidate")
    print(f"   Found {search_res.total_found} candidates.")
    assert search_res.total_found == 1
    
    print("E2E Complete and Successful.")

if __name__ == "__main__":
    run_e2e()

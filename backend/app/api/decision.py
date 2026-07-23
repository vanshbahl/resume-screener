from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.decision.services.core_engines import (decision_engine,
                                                risk_analysis_service)
from app.decision.services.gap_analysis import gap_analysis_service
from app.decision.services.recommendations import (career_recommender,
                                                   learning_recommender)
from app.intelligence.matching_service import matching_service
from app.intelligence.scoring_service import scoring_service
from app.schemas.decision import (CareerRecommendation, DecisionResult,
                                  LearningRecommendation,
                                  RiskReport)
from app.schemas.intelligence import CandidateProfile, JobProfile

router = APIRouter(prefix="/decision", tags=["Recommendation & Decision"])


class DecisionRequest(BaseModel):
    candidate: CandidateProfile
    job: JobProfile


@router.post("/hire", response_model=DecisionResult)
def make_hiring_decision(request: DecisionRequest):
    """Generates a deterministic hiring decision (e.g. Strong Hire)."""
    # 1. Match and Score
    match_res = matching_service.match(
        candidate_id=request.candidate.candidate_id,
        job_id=request.job.job_id,
        candidate_vec=request.candidate.vector,
        req_vec=request.job.required_vector,
        pref_vec=request.job.preferred_vector,
    )
    score_res = scoring_service.score_match(match_res)

    # 2. Risk Analysis
    risk = risk_analysis_service.analyze_risks(request.candidate, request.job)

    # 3. Decision
    return decision_engine.make_decision(score_res, risk)


@router.post("/analysis/risk", response_model=RiskReport)
def analyze_risk(request: DecisionRequest):
    """Standalone risk analysis."""
    return risk_analysis_service.analyze_risks(request.candidate, request.job)


@router.post("/recommend/learning", response_model=List[LearningRecommendation])
def recommend_learning(request: DecisionRequest):
    """Generates actionable learning recommendations based on gaps."""
    gap = gap_analysis_service.analyze_gap(
        candidate_id=request.candidate.candidate_id,
        job_id=request.job.job_id,
        candidate_vec=request.candidate.vector,
        req_vec=request.job.required_vector,
        pref_vec=request.job.preferred_vector,
    )
    return learning_recommender.generate_recommendations(gap)


@router.post("/recommend/career", response_model=List[CareerRecommendation])
def recommend_career(candidate: CandidateProfile):
    """Generates career movement recommendations."""
    return career_recommender.generate_recommendations(candidate)

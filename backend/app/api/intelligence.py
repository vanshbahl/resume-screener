from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any

from app.schemas.intelligence import (
    CandidateProfile, JobProfile, ScoreResult, Insight, 
    GapAnalysis, Recommendation, RankingResult
)
from app.intelligence.feature_vector_service import feature_vector_service
from app.intelligence.matching_service import matching_service
from app.intelligence.scoring_service import scoring_service
from app.intelligence.insight_service import insight_service
from app.intelligence.gap_analysis_service import gap_analysis_service
from app.intelligence.recommendation_service import recommendation_service
from app.intelligence.ranking_service import ranking_service

router = APIRouter(prefix="/intelligence", tags=["Intelligence Engine"])

class MatchRequest(BaseModel):
    candidate: CandidateProfile
    job: JobProfile

class RankingRequest(BaseModel):
    job: JobProfile
    candidates: List[CandidateProfile]

class GenericRankingRequest(BaseModel):
    items: List[Dict[str, float]]
    context: str

@router.post("/match", response_model=ScoreResult)
def match_candidate_to_job(request: MatchRequest):
    """Deterministically match and score a candidate against a job."""
    try:
        match_res = matching_service.match(
            candidate_id=request.candidate.candidate_id,
            job_id=request.job.job_id,
            candidate_vec=request.candidate.vector,
            req_vec=request.job.required_vector,
            pref_vec=request.job.preferred_vector
        )
        
        score_res = scoring_service.score_match(match_res)
        return score_res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rank", response_model=RankingResult)
def rank_candidates(request: RankingRequest):
    """Rank multiple candidates for a specific job."""
    score_results = []
    for cand in request.candidates:
        match_res = matching_service.match(
            candidate_id=cand.candidate_id,
            job_id=request.job.job_id,
            candidate_vec=cand.vector,
            req_vec=request.job.required_vector,
            pref_vec=request.job.preferred_vector
        )
        score_results.append(scoring_service.score_match(match_res))
        
    return ranking_service.rank_candidates_for_job(request.job.job_id, score_results)

@router.post("/rank/generic", response_model=RankingResult)
def rank_generic(request: GenericRankingRequest):
    """Rank arbitrary items based on provided scores."""
    return ranking_service.rank_generic(request.items, request.context)

@router.post("/insights", response_model=List[Insight])
def generate_insights(candidate: CandidateProfile):
    """Generate heuristic-based insights for a candidate."""
    return insight_service.generate_insights(candidate.vector)

class GapAnalysisResponse(BaseModel):
    analysis: GapAnalysis
    recommendations: List[Recommendation]

@router.post("/gap-analysis", response_model=GapAnalysisResponse)
def analyze_gap(request: MatchRequest):
    """Perform deterministic gap analysis and generate actionable recommendations."""
    gap_res = gap_analysis_service.analyze_gap(
        candidate_id=request.candidate.candidate_id,
        job_id=request.job.job_id,
        candidate_vec=request.candidate.vector,
        req_vec=request.job.required_vector,
        pref_vec=request.job.preferred_vector
    )
    
    recs = recommendation_service.generate_recommendations(gap_res)
    
    return GapAnalysisResponse(analysis=gap_res, recommendations=recs)

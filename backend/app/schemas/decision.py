from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.schemas.intelligence import Explanation, GapAnalysis

# ---------------------------------------------------------
# Risk Analysis Models
# ---------------------------------------------------------

class RiskItem(BaseModel):
    risk_type: str # e.g., "job_hopping", "skill_mismatch", "overqualified"
    severity: str # "low", "medium", "high", "critical"
    description: str
    evidence: str

class RiskReport(BaseModel):
    candidate_id: str
    overall_risk_level: str # "low", "medium", "high", "critical"
    risks: List[RiskItem] = Field(default_factory=list)
    confidence: float

# ---------------------------------------------------------
# Recommendation Models
# ---------------------------------------------------------

class BaseRecommendation(BaseModel):
    action: str
    reason: str
    evidence: str
    estimated_score_improvement: float = 0.0
    priority: str = "medium" # "low", "medium", "high"
    estimated_difficulty: str = "medium" # "low", "medium", "high"
    confidence: float = 1.0

class LearningRecommendation(BaseRecommendation):
    skill_target: str
    learning_path: Optional[str] = None
    
class CareerRecommendation(BaseRecommendation):
    suggested_role: str
    transferable_skills: List[str] = Field(default_factory=list)
    
class HiringRecommendation(BaseRecommendation):
    candidate_category: str # "top_candidate", "backup", "hidden_gem", "high_risk"
    job_id: str
    match_score: float

class OpportunityRecommendation(BaseRecommendation):
    job_id: str
    match_score: float
    alignment_reason: str

# ---------------------------------------------------------
# Decision Models
# ---------------------------------------------------------

class DecisionResult(BaseModel):
    target_id: str
    job_id: Optional[str] = None
    decision: str # "Strong Hire", "Hire", "Consider", "Needs Review", "Reject"
    reason: str
    confidence: float
    evidence: List[Explanation] = Field(default_factory=list)
    matched_requirements: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    risk_report: Optional[RiskReport] = None

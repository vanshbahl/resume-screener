from abc import ABC, abstractmethod

from app.schemas.decision import DecisionResult, RiskReport
from app.schemas.intelligence import CandidateProfile, JobProfile, ScoreResult


class BaseDecisionEngine(ABC):
    """Abstract base for making hiring decisions."""

    @abstractmethod
    def make_decision(
        self, score_result: ScoreResult, risk_report: RiskReport = None
    ) -> DecisionResult:
        """Evaluates scores and risks to produce a deterministic or AI-driven decision."""
        pass


class BaseRiskAnalysisService(ABC):
    """Abstract base for detecting candidate risks."""

    @abstractmethod
    def analyze_risks(
        self, candidate: CandidateProfile, job: JobProfile = None
    ) -> RiskReport:
        """Analyzes profile for red flags (job hopping, mismatches)."""
        pass

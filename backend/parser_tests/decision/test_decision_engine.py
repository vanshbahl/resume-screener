
from app.decision.services.core_engines import decision_engine
from app.schemas.decision import RiskReport
from app.schemas.intelligence import ScoreResult


def test_decision_engine_strong_hire():
    score = ScoreResult(
        candidate_id="c1",
        job_id="j1",
        overall_score=90.0,
        category_scores={},
        explanations=[],
    )
    risk = RiskReport(
        candidate_id="c1", overall_risk_level="low", risks=[], confidence=1.0
    )

    result = decision_engine.make_decision(score, risk)
    assert result.decision == "Strong Hire"


def test_decision_engine_risk_penalty():
    score = ScoreResult(
        candidate_id="c1",
        job_id="j1",
        overall_score=80.0,
        category_scores={},
        explanations=[],
    )
    risk = RiskReport(
        candidate_id="c1", overall_risk_level="high", risks=[], confidence=1.0
    )

    # Base 80 - 15 (high risk penalty) = 65 -> Hire -> Wait, threshold for Hire is 70, Consider is 55. So 65 is Consider.
    result = decision_engine.make_decision(score, risk)
    assert result.decision == "Consider"
    assert "penalty" in result.reason.lower()


def test_decision_engine_critical_rejection():
    score = ScoreResult(
        candidate_id="c1",
        job_id="j1",
        overall_score=95.0,
        category_scores={},
        explanations=[],
    )
    risk = RiskReport(
        candidate_id="c1", overall_risk_level="critical", risks=[], confidence=1.0
    )

    result = decision_engine.make_decision(score, risk)
    assert result.decision == "Reject"

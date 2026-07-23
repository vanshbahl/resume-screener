from typing import List, Dict, Any
from app.decision.base import BaseDecisionEngine, BaseRiskAnalysisService
from app.schemas.decision import DecisionResult, RiskReport, RiskItem
from app.schemas.intelligence import ScoreResult, CandidateProfile, JobProfile, Explanation
from app.parsers.core.config_loader import load_config

class RiskAnalysisService(BaseRiskAnalysisService):
    def __init__(self):
        config = load_config("recommendation/risk_rules.yaml")
        self.rules = config if isinstance(config, dict) else {}
        
    def analyze_risks(self, candidate: CandidateProfile, job: JobProfile = None) -> RiskReport:
        risks = []
        
        # 1. Job Hopping heuristic (mocked extraction, usually relies on parsed experience dates)
        jh_rules = self.rules.get("job_hopping", {})
        # Assuming we can infer short tenures from years_experience / project counts
        if candidate.vector.years_experience > 0 and len(candidate.vector.skills) > 30 and candidate.vector.years_experience < 2.0:
            risks.append(RiskItem(
                risk_type="job_hopping",
                severity=jh_rules.get("severity", "medium"),
                description="High volume of skills claimed in a very short overall tenure.",
                evidence=f"{len(candidate.vector.skills)} skills vs {candidate.vector.years_experience} YOE."
            ))
            
        # 2. Overqualification
        oq_rules = self.rules.get("overqualification", {})
        if job and job.required_vector.years_experience > 0:
            excess = candidate.vector.years_experience - job.required_vector.years_experience
            max_excess = oq_rules.get("max_excess_experience_years", 7.0)
            if excess >= max_excess:
                risks.append(RiskItem(
                    risk_type="overqualified",
                    severity=oq_rules.get("severity", "low"),
                    description=f"Candidate has significantly more experience ({candidate.vector.years_experience} YOE) than required.",
                    evidence=f"Exceeds requirement by {excess} years."
                ))
                
        # 3. Skill Mismatch (missing core)
        sm_rules = self.rules.get("skill_mismatch", {})
        if job and job.required_vector.skills:
            req_set = set(job.required_vector.skills)
            cand_set = set(candidate.vector.skills)
            matched = len(req_set.intersection(cand_set))
            match_percent = (matched / len(req_set)) * 100
            if match_percent < sm_rules.get("min_core_skills_percent", 30.0):
                risks.append(RiskItem(
                    risk_type="skill_mismatch",
                    severity=sm_rules.get("severity", "high"),
                    description="Candidate is missing the majority of core required skills.",
                    evidence=f"Matched only {matched}/{len(req_set)} core skills."
                ))

        overall_risk = "low"
        severities = [r.severity for r in risks]
        if "critical" in severities:
            overall_risk = "critical"
        elif "high" in severities:
            overall_risk = "high"
        elif "medium" in severities:
            overall_risk = "medium"

        return RiskReport(
            candidate_id=candidate.candidate_id,
            overall_risk_level=overall_risk,
            risks=risks,
            confidence=0.85
        )

class DecisionEngine(BaseDecisionEngine):
    def __init__(self):
        config = load_config("recommendation/decision_thresholds.yaml")
        if isinstance(config, dict):
            self.thresholds = config.get("thresholds", {})
            self.adjustments = config.get("risk_adjustments", {})
        else:
            self.thresholds = {"strong_hire": 85.0, "hire": 70.0, "consider": 55.0, "needs_review": 40.0}
            self.adjustments = {"high_risk_penalty": -15.0, "critical_risk_rejection": True}
            
    def make_decision(self, score_result: ScoreResult, risk_report: RiskReport = None) -> DecisionResult:
        adjusted_score = score_result.overall_score
        reason_parts = [f"Initial Score: {adjusted_score}%."]
        
        # Apply risk adjustments
        if risk_report:
            if risk_report.overall_risk_level == "critical" and self.adjustments.get("critical_risk_rejection"):
                decision = "Reject"
                reason = "Rejected due to critical risk flags."
                return DecisionResult(
                    target_id=score_result.candidate_id,
                    job_id=score_result.job_id,
                    decision=decision,
                    reason=reason,
                    confidence=1.0,
                    evidence=[Explanation(category="risk", matched_entities=[], missing_entities=[], confidence=1.0, reason=reason, evidence="Critical risk detected")],
                    risk_report=risk_report
                )
            
            if risk_report.overall_risk_level == "high":
                penalty = self.adjustments.get("high_risk_penalty", -15.0)
                adjusted_score += penalty
                reason_parts.append(f"Applied {penalty} penalty due to high risk.")
                
        # Determine Decision
        if adjusted_score >= self.thresholds.get("strong_hire", 85.0):
            decision = "Strong Hire"
        elif adjusted_score >= self.thresholds.get("hire", 70.0):
            decision = "Hire"
        elif adjusted_score >= self.thresholds.get("consider", 55.0):
            decision = "Consider"
        elif adjusted_score >= self.thresholds.get("needs_review", 40.0):
            decision = "Needs Review"
        else:
            decision = "Reject"
            
        reason_parts.append(f"Final Decision: {decision}.")
        
        return DecisionResult(
            target_id=score_result.candidate_id,
            job_id=score_result.job_id,
            decision=decision,
            reason=" ".join(reason_parts),
            confidence=0.9, # Heuristic confidence
            evidence=score_result.explanations,
            risk_report=risk_report
        )

# Singleton instances
risk_analysis_service = RiskAnalysisService()
decision_engine = DecisionEngine()

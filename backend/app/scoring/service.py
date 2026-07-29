"""Resume Scoring Service for Phase 3.

Orchestrates declarative rule evaluation, aggregates category weights, computes
overall 0-100 score, tracks rule traces, and persists ResumeScore.
"""

import logging
from typing import Any, Dict, Optional

from app.intelligence.models import CandidateProfile
from app.parsers.core.config_loader import load_config
from app.scoring.evaluator import evaluate_all_sections
from app.scoring.models import ResumeScore, ScoreDeltaType, SectionScore

logger = logging.getLogger(__name__)


class ResumeScoringService:
    """Service layer for deterministic resume scoring."""

    def __init__(self, config_name: str = "scoring_rules.yaml"):
        self.config_name = config_name

    def calculate_score(
        self,
        candidate_id: str,
        resume_id: str,
        profile: CandidateProfile,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> ResumeScore:
        """Computes a deterministic, transparent 0-100 ResumeScore for a CandidateProfile."""
        if config_override:
            rules_config = config_override
        else:
            raw = load_config(self.config_name)
            rules_config = raw if isinstance(raw, dict) else {}

        version = rules_config.get("scoring", {}).get("version", "3.0.0")

        # 1. Declarative Rule Evaluation
        section_scores, traces = evaluate_all_sections(profile, rules_config)

        # 2. Weighted Aggregation
        raw_total = sum(sec.weighted_score for sec in section_scores.values())
        overall_score = min(100.0, max(0.0, round(raw_total, 1)))

        # 3. Derive Strengths and Weaknesses from Traces & Section Scores
        strengths = [
            t.reason for t in traces if t.delta_type == ScoreDeltaType.BONUS and t.points >= 15.0
        ]
        weaknesses = [
            t.reason for t in traces if t.delta_type == ScoreDeltaType.DEDUCTION
        ]

        # Add section score highlights
        for key, sec in section_scores.items():
            if sec.raw_score >= 85.0:
                strengths.append(f"High performing {key.replace('_', ' ')} section ({sec.raw_score}/100)")
            elif sec.raw_score < 50.0:
                weaknesses.append(f"Opportunity for improvement in {key.replace('_', ' ')} ({sec.raw_score}/100)")

        # 4. Construct Canonical ResumeScore
        return ResumeScore(
            candidate_id=candidate_id,
            resume_id=resume_id,
            overall_score=overall_score,
            section_scores=section_scores,
            strengths=sorted(list(set(strengths))),
            weaknesses=sorted(list(set(weaknesses))),
            traces=traces,
            confidence=1.0,
            scoring_version=version,
            metadata={
                "rules_evaluated_count": len(traces),
                "sections_count": len(section_scores),
            },
        )


# Singleton instance
resume_scoring_service = ResumeScoringService()

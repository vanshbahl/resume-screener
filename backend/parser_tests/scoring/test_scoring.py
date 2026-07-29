"""Tests for Phase 3 Deterministic Resume Scoring Engine.

Verifies declarative rule evaluation, rule ID traceability, weighted score aggregation,
reproducibility, score bounds, and canonical ResumeScore model output.
"""

import pytest

from app.intelligence.models import (
    CandidateProfile,
    DetectedGap,
    EducationSummary,
    ExperienceSummary,
    ProjectDetail,
)
from app.scoring.evaluator import evaluate_all_sections
from app.scoring.models import ResumeScore, ScoreDeltaType, ScoreTraceItem, ScoringCategory
from app.scoring.service import resume_scoring_service


# ---------------------------------------------------------------------------
# Sample Test Fixtures
# ---------------------------------------------------------------------------

def _sample_profile() -> CandidateProfile:
    return CandidateProfile(
        candidate_id="cand-test-123",
        resume_id="res-test-456",
        primary_domain="Backend Engineering",
        career_stage="Mid-level",
        education_stream="Computer Science",
        current_experience_level="Mid",
        target_roles=["Backend Developer", "Software Engineer"],
        industry="Technology",
        seniority="Mid-Level",
        technical_specialization="API Microservices",
        normalized_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
        normalized_technologies=["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
        normalized_companies=["Acme Corp", "Beta Tech"],
        normalized_institutions=["Massachusetts Institute Of Technology"],
        normalized_certifications=["AWS Certified Solutions Architect"],
        projects=[
            ProjectDetail(
                name="High-Scale Search API",
                complexity="High",
                scale="Large Scale",
                modernity="Modern",
                tech_stack_maturity="Production-Grade",
            ),
            ProjectDetail(
                name="Analytics Dashboard",
                complexity="Medium",
                scale="Medium",
                modernity="Modern",
                tech_stack_maturity="Intermediate",
            ),
        ],
        experience_summary=ExperienceSummary(
            total_years_experience=3.5,
            relevant_years_experience=3.5,
            growth_trajectory="Steady",
            responsibility_level="Senior Contributor",
        ),
        education_summary=EducationSummary(
            highest_qualification="bachelors",
            education_stream="Computer Science",
            graduation_status="Completed",
            institutions=["Massachusetts Institute Of Technology"],
        ),
        strengths=["Broad skill set", "Hands-on projects"],
        weaknesses=[],
        detected_gaps=[],  # Clean profile with no gaps
    )


# ---------------------------------------------------------------------------
# Rule Evaluator Tests
# ---------------------------------------------------------------------------

class TestRuleEvaluator:
    def test_evaluate_all_sections_produces_traces_and_scores(self):
        profile = _sample_profile()
        rules_config = {
            "scoring": {
                "version": "3.0.0",
                "weights": {
                    "contact_structure": 0.10,
                    "education": 0.15,
                    "experience": 0.25,
                    "projects": 0.20,
                    "skills": 0.20,
                    "writing_quality": 0.10,
                },
                "rules": {
                    "contact_structure": [
                        {"rule_id": "RULE_CONTACT_EMAIL", "points": 30.0, "description": "Email present"},
                        {"rule_id": "RULE_CONTACT_PHONE", "points": 20.0, "description": "Phone present"},
                        {"rule_id": "RULE_CONTACT_LINKEDIN", "points": 25.0, "description": "LinkedIn present"},
                        {"rule_id": "RULE_CONTACT_GITHUB", "points": 25.0, "description": "GitHub present"},
                    ],
                    "education": {
                        "qualifications": {
                            "bachelors": {"points": 80.0, "rule_id": "RULE_EDU_QUAL_BACHELORS", "description": "Bachelor's degree"}
                        },
                        "bonuses": [{"rule_id": "RULE_EDU_STATUS_COMPLETED", "points": 10.0, "description": "Completed"}],
                    },
                    "experience": {
                        "yoe_base_multiplier": 15.0,
                        "yoe_cap": 80.0,
                        "yoe_rule_id": "RULE_EXP_TENURE",
                        "trajectory_bonuses": {
                            "Steady": {"points": 10.0, "rule_id": "RULE_EXP_TRAJECTORY_STEADY", "description": "Steady growth"}
                        },
                    },
                    "projects": {
                        "points_per_project": 25.0,
                        "project_cap": 70.0,
                        "project_rule_id": "RULE_PROJ_VOLUME",
                        "complexity_bonuses": {
                            "High": {"points": 10.0, "rule_id": "RULE_PROJ_COMPLEXITY_HIGH", "description": "High complexity"}
                        },
                    },
                    "skills": {
                        "points_per_skill": 5.0,
                        "skills_cap": 80.0,
                        "skill_rule_id": "RULE_SKILL_PORTFOLIO",
                        "certification_bonus_per_item": 10.0,
                        "certification_cap": 20.0,
                        "certification_rule_id": "RULE_SKILL_CERTIFICATION_BONUS",
                    },
                    "writing_quality": {
                        "metrics_present_bonus": 40.0,
                        "metrics_rule_id": "RULE_QUALITY_METRICS_PRESENT",
                        "no_critical_gaps_bonus": 30.0,
                        "no_gaps_rule_id": "RULE_QUALITY_NO_CRITICAL_GAPS",
                    },
                },
            }
        }

        section_scores, traces = evaluate_all_sections(profile, rules_config)

        assert "contact_structure" in section_scores
        assert "experience" in section_scores
        assert len(traces) > 0

        # Check rule_id attachment
        rule_ids = [t.rule_id for t in traces]
        assert "RULE_CONTACT_EMAIL" in rule_ids
        assert "RULE_EDU_QUAL_BACHELORS" in rule_ids
        assert "RULE_EXP_TENURE" in rule_ids


# ---------------------------------------------------------------------------
# Scoring Service Tests
# ---------------------------------------------------------------------------

class TestResumeScoringService:
    def test_calculate_score_returns_valid_resume_score(self):
        profile = _sample_profile()
        score = resume_scoring_service.calculate_score("cand-123", "res-456", profile)

        assert isinstance(score, ResumeScore)
        assert score.candidate_id == "cand-123"
        assert score.resume_id == "res-456"
        assert 0.0 <= score.overall_score <= 100.0
        assert score.scoring_version == "3.0.0"
        assert len(score.section_scores) == 6
        assert len(score.traces) > 0

    def test_score_is_reproducible_and_deterministic(self):
        profile = _sample_profile()
        score1 = resume_scoring_service.calculate_score("cand-123", "res-456", profile)
        score2 = resume_scoring_service.calculate_score("cand-123", "res-456", profile)

        assert score1.overall_score == score2.overall_score
        assert [t.rule_id for t in score1.traces] == [t.rule_id for t in score2.traces]

    def test_deductions_tracked_for_gaps(self):
        profile = _sample_profile()
        profile.detected_gaps.append(
            DetectedGap(gap_type="employment_gap", severity="warning", description="Gap > 6 months")
        )

        score = resume_scoring_service.calculate_score("cand-123", "res-456", profile)
        deductions = [t for t in score.traces if t.delta_type == ScoreDeltaType.DEDUCTION]

        assert len(deductions) >= 1
        assert deductions[0].rule_id == "RULE_EXP_EMPLOYMENT_GAP"
        assert deductions[0].points < 0.0

    def test_score_bounded_between_0_and_100(self):
        empty_profile = CandidateProfile(
            candidate_id="empty",
            resume_id="empty",
        )
        score = resume_scoring_service.calculate_score("empty", "empty", empty_profile)
        assert 0.0 <= score.overall_score <= 100.0

        for sec in score.section_scores.values():
            assert 0.0 <= sec.raw_score <= 100.0
            assert 0.0 <= sec.weighted_score <= 100.0

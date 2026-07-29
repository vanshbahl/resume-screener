"""Tests for Phase 2 Resume Intelligence Engine.

Verifies deterministic normalization, experience/education analysis, gap detection,
qualitative evaluation, and canonical CandidateProfile generation.
"""

import pytest

from app.intelligence.analyzer import analyze_education, analyze_experience, detect_gaps
from app.intelligence.evaluator import evaluate_qualitative_profile
from app.intelligence.models import CandidateProfile, DetectedGap, EducationSummary, ExperienceSummary
from app.intelligence.normalizer import (
    normalize_company,
    normalize_degree,
    normalize_entities,
    normalize_institution,
    normalize_skill,
    normalize_skills,
)
from app.intelligence.service import resume_intelligence_service


# ---------------------------------------------------------------------------
# Sample Test Fixtures
# ---------------------------------------------------------------------------

def _field(value: str) -> dict:
    return {"value": value, "confidence": 0.9}


def _sample_parsed_resume() -> dict:
    return {
        "personal_info": {
            "name": _field("Alex Developer"),
            "email": _field("alex@example.com"),
            "phone": _field("+1-555-0199"),
            "linkedin": _field("https://linkedin.com/in/alexdev"),
            "github": _field("https://github.com/alexdev"),
        },
        "skills": [_field("python"), _field("fastapi"), _field("react"), _field("docker")],
        "frameworks": [_field("django")],
        "tools": [_field("git"), _field("docker")],
        "languages": [_field("python"), _field("typescript")],
        "education": [
            {
                "institution": _field("Massachusetts Institute of Technology"),
                "degree": _field("Bachelor of Science in Computer Science"),
                "graduation_year": _field("2021"),
            }
        ],
        "experience": [
            {
                "company": _field("Acme Tech Inc."),
                "title": _field("Backend Engineer"),
                "duration_months": 24,
                "start_date": _field("2022-01"),
                "end_date": _field("2024-01"),
                "description": _field("Built REST APIs handling 50k requests/sec using FastAPI and PostgreSQL."),
            },
            {
                "company": _field("Beta Innovations LLC"),
                "title": _field("Junior Software Developer"),
                "duration_months": 12,
                "start_date": _field("2021-01"),
                "end_date": _field("2021-12"),
                "description": _field("Developed web applications using React and Node."),
            },
        ],
        "projects": [
            {
                "name": _field("High-Scale Vector Search Engine"),
                "description": _field("Built a microservices vector search pipeline with FastAPI and Docker."),
            }
        ],
        "certifications": [
            {"name": _field("AWS Certified Solutions Architect")}
        ],
    }


# ---------------------------------------------------------------------------
# Normalizer Tests
# ---------------------------------------------------------------------------

class TestNormalizer:
    def test_normalize_skill_canonicalization(self):
        assert normalize_skill("python") == "Python"
        assert normalize_skill("fastapi") == "FastAPI"

    def test_normalize_skills_deduplicates(self):
        raw = [_field("python"), _field("Python"), _field("fastapi")]
        res = normalize_skills(raw)
        assert "Python" in res
        assert "FastAPI" in res
        assert len(res) == 2

    def test_normalize_degree_bachelors(self):
        qual, stream = normalize_degree("Bachelor of Technology in Computer Science")
        assert qual == "bachelors"
        assert stream == "Computer Science"

    def test_normalize_degree_masters(self):
        qual, stream = normalize_degree("Master of Science in Electrical Engineering")
        assert qual == "masters"
        assert stream == "Electrical Engineering"

    def test_normalize_company_cleans_legal_suffixes(self):
        assert normalize_company("Acme Tech Inc.") == "Acme Tech"
        assert normalize_company("Beta Innovations LLC") == "Beta Innovations"

    def test_normalize_institution(self):
        assert normalize_institution("massachusetts institute of technology") == "Massachusetts Institute Of Technology"

    def test_normalize_entities_full(self):
        norm = normalize_entities(_sample_parsed_resume())
        assert "Python" in norm["normalized_skills"]
        assert "Acme Tech" in norm["normalized_companies"]
        assert "Massachusetts Institute Of Technology" in norm["normalized_institutions"]


# ---------------------------------------------------------------------------
# Analyzer Tests
# ---------------------------------------------------------------------------

class TestAnalyzer:
    def test_analyze_experience_calculates_yoe(self):
        summary = analyze_experience(_sample_parsed_resume())
        assert summary.total_years_experience == 3.0  # 24 + 12 = 36 months = 3.0 YOE

    def test_analyze_education_extracts_highest_qual(self):
        summary = analyze_education(_sample_parsed_resume())
        assert summary.highest_qualification == "bachelors"
        assert summary.education_stream == "Computer Science"

    def test_detect_gaps_identifies_clean_resume(self):
        gaps = detect_gaps(_sample_parsed_resume())
        gap_types = [g.gap_type for g in gaps]
        assert "missing_contact" not in gap_types

    def test_detect_gaps_identifies_missing_github(self):
        parsed = _sample_parsed_resume()
        parsed["personal_info"]["github"] = None
        gaps = detect_gaps(parsed)
        gap_types = [g.gap_type for g in gaps]
        assert "missing_github" in gap_types or "missing_link" in gap_types


# ---------------------------------------------------------------------------
# Evaluator Tests
# ---------------------------------------------------------------------------

class TestEvaluator:
    def test_evaluate_qualitative_profile_infers_domain(self):
        parsed = _sample_parsed_resume()
        norm = normalize_entities(parsed)
        eval_res = evaluate_qualitative_profile(parsed, norm["normalized_skills"], 3.0)

        assert eval_res["primary_domain"] in ("Backend Engineering", "Full-Stack Engineering")
        assert eval_res["career_stage"] == "Mid-level"
        assert len(eval_res["projects"]) == 1
        assert eval_res["projects"][0].complexity in ("High", "Enterprise")


# ---------------------------------------------------------------------------
# End-to-End Service Tests
# ---------------------------------------------------------------------------

class TestResumeIntelligenceService:
    def test_generate_profile_produces_valid_candidate_profile(self):
        parsed = _sample_parsed_resume()
        profile = resume_intelligence_service.generate_profile(
            candidate_id="cand-123",
            resume_id="res-456",
            parsed_metadata=parsed,
        )

        assert isinstance(profile, CandidateProfile)
        assert profile.candidate_id == "cand-123"
        assert profile.resume_id == "res-456"
        assert profile.engine_version == "2.0.0"
        assert len(profile.normalized_skills) > 0
        assert profile.experience_summary.total_years_experience == 3.0
        assert profile.education_summary.highest_qualification == "bachelors"
        assert profile.primary_domain in ("Backend Engineering", "Full-Stack Engineering")

        # Verify JSON serializability
        dump = profile.model_dump(mode="json")
        assert isinstance(dump, dict)
        assert dump["candidate_id"] == "cand-123"

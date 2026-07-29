"""Tests for the deterministic Resume Health Report.

Verifies that specific resume defects produce the expected health flags,
and that the overall_health label maps correctly to section scores.
No DB, no AI, no file I/O.
"""

import pytest

from app.parsers.health_report import generate_health_report


def _field(value):
    return {"value": value, "confidence": 0.9}


def _healthy_resume() -> dict:
    return {
        "personal_info": {
            "name": _field("Jane Doe"),
            "email": _field("jane@example.com"),
            "phone": _field("+1-555-0001"),
        },
        "education": [
            {
                "institution": _field("MIT"),
                "degree": _field("B.Sc. Computer Science"),
                "graduation_year": _field("2022"),
            }
        ],
        "experience": [
            {
                "company": _field("Acme Corp"),
                "title": _field("Software Engineer"),
                "description": _field(
                    "Led backend development\nDesigned REST APIs\nMentored junior engineers"
                ),
                "responsibilities": [_field("Code reviews"), _field("Sprint planning")],
            }
        ],
        "skills": [_field("Python"), _field("FastAPI"), _field("Docker"), _field("PostgreSQL"), _field("Redis")],
        "frameworks": [],
        "tools": [],
        "projects": [
            {"name": _field("ML Pipeline"), "description": _field("Built an end-to-end ML system.")}
        ],
    }


# ---------------------------------------------------------------------------
# Contact checks
# ---------------------------------------------------------------------------

class TestContactFlags:
    def test_missing_email_raises_error_flag(self):
        resume = _healthy_resume()
        resume["personal_info"]["email"] = None
        report = generate_health_report(resume)
        codes = [f["code"] for f in report["flags"]]
        assert "missing_email" in codes

    def test_missing_phone_raises_warning_flag(self):
        resume = _healthy_resume()
        resume["personal_info"]["phone"] = None
        report = generate_health_report(resume)
        codes = [f["code"] for f in report["flags"]]
        assert "missing_phone" in codes

    def test_missing_name_raises_error_flag(self):
        resume = _healthy_resume()
        resume["personal_info"]["name"] = None
        report = generate_health_report(resume)
        codes = [f["code"] for f in report["flags"]]
        assert "missing_name" in codes

    def test_complete_contact_has_no_flags(self):
        report = generate_health_report(_healthy_resume())
        contact_flags = [f for f in report["flags"] if f["section"] == "contact"]
        assert contact_flags == []


# ---------------------------------------------------------------------------
# Education checks
# ---------------------------------------------------------------------------

class TestEducationFlags:
    def test_missing_degree_flags_incomplete(self):
        resume = _healthy_resume()
        resume["education"][0]["degree"] = None
        report = generate_health_report(resume)
        codes = [f["code"] for f in report["flags"]]
        assert "education_incomplete" in codes

    def test_missing_graduation_year_flags_no_dates(self):
        resume = _healthy_resume()
        resume["education"][0]["graduation_year"] = None
        report = generate_health_report(resume)
        codes = [f["code"] for f in report["flags"]]
        assert "education_no_dates" in codes


# ---------------------------------------------------------------------------
# Experience checks
# ---------------------------------------------------------------------------

class TestExperienceFlags:
    def test_missing_company_flags_incomplete(self):
        resume = _healthy_resume()
        resume["experience"][0]["company"] = None
        report = generate_health_report(resume)
        codes = [f["code"] for f in report["flags"]]
        assert "experience_entry_incomplete" in codes

    def test_thin_description_flags_warning(self):
        resume = _healthy_resume()
        resume["experience"][0]["description"] = _field("Did some work")  # single line
        resume["experience"][0]["responsibilities"] = []
        report = generate_health_report(resume)
        codes = [f["code"] for f in report["flags"]]
        assert "experience_thin_description" in codes


# ---------------------------------------------------------------------------
# Skills checks
# ---------------------------------------------------------------------------

class TestSkillsFlags:
    def test_too_few_skills_flags_sparse(self):
        resume = _healthy_resume()
        resume["skills"] = [_field("Python")]  # only 1
        resume["frameworks"] = []
        resume["tools"] = []
        report = generate_health_report(resume)
        codes = [f["code"] for f in report["flags"]]
        assert "skills_sparse" in codes

    def test_sufficient_skills_no_flag(self):
        report = generate_health_report(_healthy_resume())
        codes = [f["code"] for f in report["flags"]]
        assert "skills_sparse" not in codes


# ---------------------------------------------------------------------------
# Overall health
# ---------------------------------------------------------------------------

class TestOverallHealth:
    def test_healthy_resume_scores_excellent_or_good(self):
        report = generate_health_report(_healthy_resume())
        assert report["overall_health"] in ("excellent", "good")

    def test_broken_resume_scores_fair_or_poor(self):
        """A resume with no data should generate error flags and score below excellent."""
        empty = {
            "personal_info": {},
            "education": [],
            "experience": [],
            "skills": [],
            "frameworks": [],
            "tools": [],
            "projects": [],
        }
        report = generate_health_report(empty)
        # Must have some error flags
        assert len(report["flags"]) > 0
        error_flags = [f for f in report["flags"] if f["severity"] == "error"]
        assert len(error_flags) > 0, "An empty resume should produce at least one error flag."
        # Must not score excellent
        assert report["overall_health"] != "excellent"

    def test_section_scores_in_report(self):
        report = generate_health_report(_healthy_resume())
        assert "section_scores" in report
        for section in ("contact", "education", "experience", "skills"):
            assert section in report["section_scores"]
            assert 0 <= report["section_scores"][section] <= 100

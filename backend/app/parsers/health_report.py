"""Resume Health Report Generator.

Produces a deterministic health assessment of a parsed resume by evaluating
the QUALITY of populated sections — not just their presence.

Completeness answers: "What is present?"
Health Report answers: "How well are the present sections populated?"

These are distinct analytical outputs and must remain separate.
This module has NO DB access, NO AI inference, and NO pipeline dependency.

Usage::

    from app.parsers.health_report import generate_health_report

    report = generate_health_report(structured_data_dict)
    # {
    #   "overall_health": "good",
    #   "flags": [...],
    #   "section_scores": {"contact": 80, "experience": 65, ...}
    # }
"""

import logging
from typing import Any, Dict, List, Optional

from app.parsers.core.config_loader import load_config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data types (simple dicts — no Pydantic here, this is a service output)
# ---------------------------------------------------------------------------

HealthFlag = Dict[str, str]  # {code, section, severity, detail}


def generate_health_report(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a deterministic health report for a parsed resume.

    Args:
        structured_data: The ``model_dump()`` output of ``ParsedResumeSchema``.

    Returns:
        A dict with keys:

        - ``overall_health`` (str): ``"excellent"`` / ``"good"`` / ``"fair"`` / ``"poor"``
        - ``flags`` (List[dict]): Ordered list of health flags found.
        - ``section_scores`` (dict): Per-section score (0\u2013100) for key sections.
    """
    cfg = load_config("health_report_config.yaml").get("health_report", {})
    flags: List[HealthFlag] = []

    # Run all checks
    _check_contact(structured_data, flags)
    _check_education(structured_data, flags, cfg)
    _check_experience(structured_data, flags, cfg)
    _check_skills(structured_data, flags, cfg)
    _check_projects(structured_data, flags)

    section_scores = _compute_section_scores(structured_data, flags)
    overall_health = _compute_overall_health(section_scores, cfg)

    return {
        "overall_health": overall_health,
        "flags": flags,
        "section_scores": section_scores,
    }


# ---------------------------------------------------------------------------
# Section checkers
# ---------------------------------------------------------------------------

def _get_field_value(field: Optional[Any]) -> Optional[str]:
    """Extract the string value from an ExtractedField dict or return None."""
    if isinstance(field, dict):
        return field.get("value") or None
    return field or None


def _check_contact(data: Dict[str, Any], flags: List[HealthFlag]) -> None:
    personal_info = data.get("personal_info", {})

    if not _get_field_value(personal_info.get("email")):
        flags.append({
            "code": "missing_email",
            "section": "contact",
            "severity": "error",
            "detail": "No email address detected. Email is required for candidate contact.",
        })

    if not _get_field_value(personal_info.get("phone")):
        flags.append({
            "code": "missing_phone",
            "section": "contact",
            "severity": "warning",
            "detail": "No phone number detected.",
        })

    if not _get_field_value(personal_info.get("name")):
        flags.append({
            "code": "missing_name",
            "section": "contact",
            "severity": "error",
            "detail": "Candidate name could not be extracted from the resume.",
        })


def _check_education(
    data: Dict[str, Any], flags: List[HealthFlag], cfg: Dict[str, Any]
) -> None:
    education = data.get("education", [])
    min_entries = cfg.get("min_education_entries", 1)

    if len(education) < min_entries:
        flags.append({
            "code": "education_missing",
            "section": "education",
            "severity": "error",
            "detail": "No education entries detected.",
        })
        return

    for i, entry in enumerate(education):
        has_institution = bool(_get_field_value(entry.get("institution")))
        has_degree = bool(_get_field_value(entry.get("degree")))

        if not has_institution or not has_degree:
            flags.append({
                "code": "education_incomplete",
                "section": "education",
                "severity": "warning",
                "detail": (
                    f"Education entry {i + 1} is missing "
                    f"{'institution' if not has_institution else 'degree'}. "
                    "Both are expected."
                ),
            })

        has_year = (
            _get_field_value(entry.get("graduation_year"))
            or _get_field_value(entry.get("end_date"))
            or _get_field_value(entry.get("expected_graduation"))
        )
        if not has_year:
            flags.append({
                "code": "education_no_dates",
                "section": "education",
                "severity": "info",
                "detail": f"Education entry {i + 1} has no graduation year or date.",
            })


def _check_experience(
    data: Dict[str, Any], flags: List[HealthFlag], cfg: Dict[str, Any]
) -> None:
    experience = data.get("experience", [])
    min_bullets = cfg.get("min_experience_bullets", 2)

    for i, entry in enumerate(experience):
        has_company = bool(_get_field_value(entry.get("company")))
        has_title = bool(_get_field_value(entry.get("title")))

        if not has_company or not has_title:
            flags.append({
                "code": "experience_entry_incomplete",
                "section": "experience",
                "severity": "warning",
                "detail": (
                    f"Experience entry {i + 1} is missing "
                    f"{'company' if not has_company else 'job title'}."
                ),
            })

        # Count description lines as a proxy for bullet-point richness
        desc = _get_field_value(entry.get("description"))
        responsibilities = entry.get("responsibilities", [])
        desc_lines = (desc.count("\n") + 1) if desc else 0
        total_lines = desc_lines + len(responsibilities)

        if total_lines < min_bullets:
            flags.append({
                "code": "experience_thin_description",
                "section": "experience",
                "severity": "warning",
                "detail": (
                    f"Experience entry {i + 1} has only {total_lines} description "
                    f"line(s); at least {min_bullets} are recommended."
                ),
            })


def _check_skills(
    data: Dict[str, Any], flags: List[HealthFlag], cfg: Dict[str, Any]
) -> None:
    min_count = cfg.get("min_skills_count", 5)
    skills = data.get("skills", [])
    frameworks = data.get("frameworks", [])
    tools = data.get("tools", [])
    total = len(skills) + len(frameworks) + len(tools)

    if total < min_count:
        flags.append({
            "code": "skills_sparse",
            "section": "skills",
            "severity": "warning",
            "detail": (
                f"Only {total} skill(s) detected across skills, frameworks, and tools. "
                f"At least {min_count} are recommended."
            ),
        })


def _check_projects(data: Dict[str, Any], flags: List[HealthFlag]) -> None:
    for i, project in enumerate(data.get("projects", [])):
        has_name = bool(_get_field_value(project.get("name")))
        has_desc = bool(_get_field_value(project.get("description")))

        if not has_name or not has_desc:
            flags.append({
                "code": "project_incomplete",
                "section": "projects",
                "severity": "info",
                "detail": (
                    f"Project entry {i + 1} is missing "
                    f"{'name' if not has_name else 'description'}."
                ),
            })


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _compute_section_scores(
    data: Dict[str, Any], flags: List[HealthFlag]
) -> Dict[str, int]:
    """Compute a 0–100 quality score for each key section."""

    def _section_flag_penalty(section: str) -> int:
        """Count errors and warnings in a section and compute deduction."""
        deduction = 0
        for flag in flags:
            if flag["section"] == section:
                sev = flag["severity"]
                if sev == "error":
                    deduction += 25
                elif sev == "warning":
                    deduction += 15
                elif sev == "info":
                    deduction += 5
        return min(deduction, 100)

    sections = ["contact", "education", "experience", "skills", "projects"]
    return {
        section: max(0, 100 - _section_flag_penalty(section))
        for section in sections
    }


def _compute_overall_health(
    section_scores: Dict[str, int], cfg: Dict[str, Any]
) -> str:
    """Map average section score to an overall health label."""
    if not section_scores:
        return "poor"

    avg = sum(section_scores.values()) / len(section_scores)
    thresholds = cfg.get("overall_health_thresholds", {})

    if avg >= thresholds.get("excellent", 90):
        return "excellent"
    if avg >= thresholds.get("good", 70):
        return "good"
    if avg >= thresholds.get("fair", 50):
        return "fair"
    return "poor"

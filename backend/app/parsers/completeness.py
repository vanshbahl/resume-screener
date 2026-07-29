"""Resume Completeness Analyzer.

Calculates a deterministic completeness score (0–100) for a parsed resume.
This module performs NO AI inference \u2014 only presence/absence checks.

Scoring model:
    Fields are grouped into three tiers read from ``completeness_config.yaml``:

    - **required**:    Absence deducts the full weight. Missing a phone matters more
                       than missing a portfolio.
    - **recommended**: Same weight semantics, but these fields represent competitive
                       differentiation rather than baseline requirements.
    - **optional**:    Presence adds bonus points; absence does NOT penalise.

Usage::

    from app.parsers.completeness import analyze_completeness

    result = analyze_completeness(structured_data_dict)
    # {"score": 82, "missing": [...], "tier_breakdown": {...}}
"""

import logging
from typing import Any, Dict, List

from app.parsers.core.config_loader import load_config

logger = logging.getLogger(__name__)


def _is_present(data: Dict[str, Any], key: str) -> bool:
    """Return True if the resume dict has a non-empty value for *key*.

    Handles both top-level lists (education, experience, skills…) and nested
    personal_info fields (contact_name, email, github, linkedin, portfolio).
    """
    # Personal info sub-fields
    _PERSONAL_INFO_MAP = {
        "contact_name": ("personal_info", "name"),
        "email": ("personal_info", "email"),
        "phone": ("personal_info", "phone"),
        "linkedin": ("personal_info", "linkedin"),
        "github": ("personal_info", "github"),
        "portfolio": ("personal_info", "portfolio"),
    }

    if key in _PERSONAL_INFO_MAP:
        section, sub_key = _PERSONAL_INFO_MAP[key]
        personal_info = data.get(section, {})
        field = personal_info.get(sub_key)
        if not field:
            return False
        # ExtractedField dict has a "value" key; plain dict/string also accepted.
        if isinstance(field, dict):
            return bool(field.get("value"))
        return bool(field)

    # Top-level list fields (education, experience, skills, projects, …)
    value = data.get(key)
    if value is None:
        return False
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return bool(value.get("value"))
    return bool(value)


def analyze_completeness(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a tiered completeness score for a parsed resume.

    Args:
        structured_data: The ``model_dump()`` output of ``ParsedResumeSchema``.

    Returns:
        A dict with keys:

        - ``score`` (int 0\u2013100): Weighted completeness score.
        - ``missing`` (List[str]): Human-readable labels of absent fields.
        - ``tier_breakdown`` (dict): Per-tier score/max/missing breakdown.
    """
    cfg = load_config("completeness_config.yaml").get("completeness", {})
    fields_cfg: Dict[str, Dict[str, int]] = cfg.get("fields", {})

    required_weights: Dict[str, int] = fields_cfg.get("required", {})
    recommended_weights: Dict[str, int] = fields_cfg.get("recommended", {})
    optional_weights: Dict[str, int] = fields_cfg.get("optional", {})

    total_score = 0
    missing: List[str] = []
    tier_breakdown: Dict[str, Any] = {}

    for tier_name, weights in [
        ("required", required_weights),
        ("recommended", recommended_weights),
        ("optional", optional_weights),
    ]:
        tier_score = 0
        tier_max = sum(weights.values())
        tier_missing: List[str] = []

        for field_key, weight in weights.items():
            if _is_present(structured_data, field_key):
                tier_score += weight
            else:
                tier_missing.append(_label(field_key))
                if tier_name in ("required", "recommended"):
                    missing.append(_label(field_key))

        total_score += tier_score
        tier_breakdown[tier_name] = {
            "score": tier_score,
            "max": tier_max,
            "missing": tier_missing,
        }

    return {
        "score": min(total_score, 100),
        "missing": missing,
        "tier_breakdown": tier_breakdown,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LABEL_MAP: Dict[str, str] = {
    "contact_name": "Full Name",
    "email": "Email Address",
    "phone": "Phone Number",
    "linkedin": "LinkedIn Profile",
    "github": "GitHub Profile",
    "portfolio": "Portfolio / Website",
    "education": "Education",
    "experience": "Work Experience",
    "skills": "Skills",
    "projects": "Projects",
    "certifications": "Certifications",
    "spoken_languages": "Languages",
    "summary": "Professional Summary",
    "achievements": "Achievements",
    "volunteer": "Volunteer Work",
    "leadership": "Leadership",
    "publications": "Publications",
    "activities": "Activities",
}


def _label(field_key: str) -> str:
    """Return a human-readable label for a field key."""
    return _LABEL_MAP.get(field_key, field_key.replace("_", " ").title())

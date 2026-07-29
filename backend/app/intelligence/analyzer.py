"""Deterministic Resume Analyzer for Phase 2.

Calculates experience tenure, detects employment gaps, and performs gap detection
(missing links, missing quantifiable metrics, missing dates/contact info) purely via deterministic logic.
"""

from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Tuple

from app.intelligence.models import DetectedGap, EducationSummary, ExperienceSummary
from app.intelligence.normalizer import normalize_degree

# Enhanced regex pattern for quantifiable metrics (numbers, percentages, currency, metrics)
_METRIC_PATTERN = re.compile(
    r"(\d+%\s*|\$\s*[\d,]+|\b[\d,]+\s*(x|k|m|b|percent|users|clients|requests|ms|sec|engineers|projects|applications|services)\b|\b\d{2,}\b)",
    re.IGNORECASE,
)


def _extract_val(field: Any) -> str:
    """Extract string value from ExtractedField dicts or string primitives."""
    if not field:
        return ""
    if isinstance(field, dict):
        val = field.get("value")
        if isinstance(val, str):
            return val.strip()
        if isinstance(val, dict):
            return str(val.get("value", "")).strip()
        return str(val or "").strip()
    return str(field).strip()


def _parse_year_month(date_str: str) -> Optional[Tuple[int, int]]:
    """Extracts (year, month) from date strings like '2022-01', 'Jan 2022', '2022'."""
    if not date_str:
        return None

    clean = date_str.strip().lower()
    if clean in ("present", "current", "now", "ongoing"):
        now = datetime.utcnow()
        return now.year, now.month

    # Look for 4 digit year
    year_match = re.search(r"\b(19\d\d|20\d\d)\b", clean)
    if not year_match:
        return None
    year = int(year_match.group(1))

    # Look for month
    month = 6  # Mid-year fallback
    month_names = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    for m_name, m_num in month_names.items():
        if m_name in clean:
            month = m_num
            break

    # Look for numeric month like 2022-05
    iso_match = re.search(r"\b(19\d\d|20\d\d)[-/.](0?[1-9]|1[0-2])\b", clean)
    if iso_match:
        month = int(iso_match.group(2))

    return year, month


def _calculate_exp_months(exp: Dict[str, Any]) -> float:
    """Calculates duration in months from experience entry dates or duration strings."""
    # 0. Check explicit duration_months field
    duration_months = exp.get("duration_months")
    if duration_months is not None:
        try:
            return float(duration_months)
        except (ValueError, TypeError):
            pass
    start_raw = _extract_val(exp.get("start_date"))
    end_raw = _extract_val(exp.get("end_date"))

    start_ym = _parse_year_month(start_raw)
    end_ym = _parse_year_month(end_raw)

    if start_ym:
        end_y, end_m = end_ym if end_ym else (datetime.utcnow().year, datetime.utcnow().month)
        start_y, start_m = start_ym
        # HR inclusive tenure: (end_year - start_year)*12 + (end_month - start_month) + 1
        months = (end_y - start_y) * 12 + (end_m - start_m) + 1
        if months > 0:
            return float(months)

    # 2. Fallback: Parse explicit duration string (e.g. "12 months", "2 years")
    dur_raw = _extract_val(exp.get("duration"))
    if dur_raw:
        yr_match = re.search(r"(\d+(?:\.\d+)?)\s*year", dur_raw, re.I)
        if yr_match:
            return float(yr_match.group(1)) * 12.0

        mo_match = re.search(r"(\d+(?:\.\d+)?)\s*month", dur_raw, re.I)
        if mo_match:
            return float(mo_match.group(1))

    # 3. Default estimate per experience entry if description exists
    if exp.get("company") or exp.get("title") or exp.get("description"):
        return 12.0  # Default 1 year per experience entry if dates absent

    return 0.0


def analyze_experience(parsed_resume: Dict[str, Any]) -> ExperienceSummary:
    """Calculates total YoE and checks structural experience patterns."""
    experiences = parsed_resume.get("experience", [])
    total_months = 0.0

    for exp in experiences:
        if isinstance(exp, dict):
            total_months += _calculate_exp_months(exp)

    total_years = round(total_months / 12.0, 1)

    # Growth trajectory heuristic
    growth_trajectory = "Steady"
    if total_years >= 4.0 or len(experiences) >= 3:
        growth_trajectory = "Accelerated"
    elif total_years < 1.0:
        growth_trajectory = "Early Career"

    return ExperienceSummary(
        total_years_experience=total_years,
        relevant_years_experience=total_years,
        growth_trajectory=growth_trajectory,
        responsibility_level="Individual Contributor" if total_years < 4.0 else "Senior Contributor",
    )


def analyze_education(parsed_resume: Dict[str, Any]) -> EducationSummary:
    """Determines highest qualification and stream deterministically."""
    education_entries = parsed_resume.get("education", [])
    highest_qual = "bachelors"
    stream = "Computer Science"
    institutions = []

    level_rank = {"high_school": 1, "diploma": 2, "bachelors": 3, "masters": 4, "phd": 5}
    current_max_rank = 0

    for edu in education_entries:
        if isinstance(edu, dict):
            deg_str = _extract_val(edu.get("degree")) or _extract_val(edu.get("field_of_study"))
            qual, strm = normalize_degree(deg_str)
            rank = level_rank.get(qual, 3)

            if rank > current_max_rank:
                current_max_rank = rank
                highest_qual = qual
                stream = strm

            inst_name = _extract_val(edu.get("institution"))
            if inst_name:
                institutions.append(inst_name.title())

    return EducationSummary(
        highest_qualification=highest_qual,
        education_stream=stream,
        graduation_status="Completed" if education_entries else "Unknown",
        institutions=sorted(list(set(institutions))),
    )


def detect_gaps(parsed_resume: Dict[str, Any]) -> List[DetectedGap]:
    """Scans parsed metadata to identify missing info and formatting/content gaps."""
    gaps: List[DetectedGap] = []
    personal_info = parsed_resume.get("personal_info", {}) or {}

    # 1. Granular Contact Gaps
    email_val = _extract_val(personal_info.get("email"))
    if not email_val:
        gaps.append(DetectedGap(gap_type="missing_email", severity="critical", description="Missing contact email address."))

    phone_val = _extract_val(personal_info.get("phone"))
    if not phone_val:
        gaps.append(DetectedGap(gap_type="missing_phone", severity="warning", description="Missing phone number."))

    linkedin_val = _extract_val(personal_info.get("linkedin"))
    if not linkedin_val:
        gaps.append(DetectedGap(gap_type="missing_linkedin", severity="info", description="Missing LinkedIn profile URL."))

    github_val = _extract_val(personal_info.get("github"))
    if not github_val:
        gaps.append(DetectedGap(gap_type="missing_github", severity="info", description="Missing GitHub repository link."))

    # 2. Project Gaps
    projects = parsed_resume.get("projects", [])
    if not projects:
        gaps.append(DetectedGap(gap_type="missing_projects", severity="warning", description="No portfolio projects listed."))
    else:
        for idx, proj in enumerate(projects):
            desc_val = _extract_val(proj.get("description")) if isinstance(proj, dict) else ""
            if not desc_val or len(desc_val.strip()) < 15:
                gaps.append(
                    DetectedGap(
                        gap_type="missing_project_description",
                        severity="warning",
                        description=f"Project #{idx+1} has thin or missing description.",
                    )
                )

    # 3. Measurable Metrics Check
    experiences = parsed_resume.get("experience", [])
    has_metrics = False
    for exp in experiences:
        if isinstance(exp, dict):
            desc_val = _extract_val(exp.get("description"))
            if _METRIC_PATTERN.search(desc_val):
                has_metrics = True
                break

    if experiences and not has_metrics:
        gaps.append(
            DetectedGap(
                gap_type="missing_metrics",
                severity="warning",
                description="Work experience descriptions lack quantifiable achievements or metrics (e.g. %, $, numbers).",
            )
        )

    # 4. Employment Dates Check
    for idx, exp in enumerate(experiences):
        if isinstance(exp, dict):
            start = _extract_val(exp.get("start_date"))
            if not start:
                gaps.append(
                    DetectedGap(
                        gap_type="missing_dates",
                        severity="warning",
                        description=f"Experience entry #{idx+1} is missing start date.",
                    )
                )

    return gaps

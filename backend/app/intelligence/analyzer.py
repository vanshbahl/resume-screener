"""Deterministic Resume Analyzer for Phase 2.

Calculates experience tenure, detects employment gaps, and performs gap detection
(missing links, missing quantifiable metrics, missing dates/contact info) purely via deterministic logic.
"""

import re
from typing import Any, Dict, List, Tuple

from app.intelligence.models import DetectedGap, EducationSummary, ExperienceSummary
from app.intelligence.normalizer import normalize_degree

# Regex pattern for quantifiable metrics (numbers, percentages, dollar amounts)
_METRIC_PATTERN = re.compile(r"(\d+%\s*|\$\s*\d+|\b\d+\s*(x|k|m|b|percent|users|clients|requests|ms|sec)\b|\b\d{2,}\b)", re.IGNORECASE)


def analyze_experience(parsed_resume: Dict[str, Any]) -> ExperienceSummary:
    """Calculates total YoE and checks structural experience patterns."""
    experiences = parsed_resume.get("experience", [])
    total_months = 0.0

    for exp in experiences:
        if isinstance(exp, dict):
            duration = exp.get("duration_months")
            if duration:
                try:
                    total_months += float(duration)
                except (ValueError, TypeError):
                    pass

    total_years = round(total_months / 12, 1)

    # Deterministic trajectory heuristic
    growth_trajectory = "Steady"
    if total_years > 5 and len(experiences) >= 3:
        growth_trajectory = "Accelerated"
    elif total_years < 1:
        growth_trajectory = "Early Career"

    return ExperienceSummary(
        total_years_experience=total_years,
        relevant_years_experience=total_years,
        growth_trajectory=growth_trajectory,
        responsibility_level="Individual Contributor" if total_years < 5 else "Senior Contributor",
    )


def analyze_education(parsed_resume: Dict[str, Any]) -> EducationSummary:
    """Determines highest qualification and stream deterministically."""
    education_entries = parsed_resume.get("education", [])
    highest_qual = "bachelors"
    stream = "General"
    institutions = []

    level_rank = {"high_school": 1, "diploma": 2, "bachelors": 3, "masters": 4, "phd": 5}
    current_max_rank = 0

    for edu in education_entries:
        if isinstance(edu, dict):
            deg_val = edu.get("degree")
            deg_str = deg_val.get("value", "") if isinstance(deg_val, dict) else str(deg_val or "")

            qual, strm = normalize_degree(deg_str)
            rank = level_rank.get(qual, 3)

            if rank > current_max_rank:
                current_max_rank = rank
                highest_qual = qual
                stream = strm

            inst_val = edu.get("institution")
            inst_name = inst_val.get("value", "") if isinstance(inst_val, dict) else str(inst_val or "")
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

    # 1. Contact Gaps
    email = personal_info.get("email")
    email_val = email.get("value") if isinstance(email, dict) else email
    if not email_val:
        gaps.append(DetectedGap(gap_type="missing_contact", severity="critical", description="Missing contact email address."))

    phone = personal_info.get("phone")
    phone_val = phone.get("value") if isinstance(phone, dict) else phone
    if not phone_val:
        gaps.append(DetectedGap(gap_type="missing_contact", severity="warning", description="Missing phone number."))

    linkedin = personal_info.get("linkedin")
    linkedin_val = linkedin.get("value") if isinstance(linkedin, dict) else linkedin
    if not linkedin_val:
        gaps.append(DetectedGap(gap_type="missing_link", severity="info", description="Missing LinkedIn profile URL."))

    github = personal_info.get("github")
    github_val = github.get("value") if isinstance(github, dict) else github
    if not github_val:
        gaps.append(DetectedGap(gap_type="missing_link", severity="info", description="Missing GitHub or code repository link."))

    # 2. Project Gaps
    projects = parsed_resume.get("projects", [])
    if not projects:
        gaps.append(DetectedGap(gap_type="missing_projects", severity="warning", description="No portfolio projects listed."))
    else:
        for idx, proj in enumerate(projects):
            desc = proj.get("description")
            desc_val = desc.get("value", "") if isinstance(desc, dict) else str(desc or "")
            if not desc_val or len(desc_val.strip()) < 20:
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
        desc = exp.get("description")
        desc_val = desc.get("value", "") if isinstance(desc, dict) else str(desc or "")
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

    # 4. Dates Check
    for idx, exp in enumerate(experiences):
        start = exp.get("start_date")
        if not start:
            gaps.append(
                DetectedGap(
                    gap_type="missing_dates",
                    severity="warning",
                    description=f"Experience entry #{idx+1} is missing start date.",
                )
            )

    return gaps

"""Deterministic Entity Normalizer for Phase 2.

Normalizes skills, technologies, degrees, education streams, companies, and institutions
without external AI calls. Uses OntologyService and deterministic pattern mapping.
"""

import re
from typing import Any, Dict, List, Tuple

from app.intelligence.ontology_service import ontology_service

# Clean suffix regex for companies
_COMPANY_SUFFIXES = re.compile(
    r"\b(inc|inc\.|llc|ltd|pvt\.|pvt|corp|corporation|co\.|co|gmbh)\b", re.IGNORECASE
)

# Degree pattern mapping: (regex pattern, qualification, stream)
_DEGREE_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (re.compile(r"\b(ph\.?d|doctor|doctorate)\b", re.I), "phd", "Research"),
    (re.compile(r"\b(m\.?s|master|m\.?tech|m\.?e|mba)\b", re.I), "masters", "Computer Science"),
    (re.compile(r"\b(b\.?s|bachelor|b\.?tech|b\.?e|b\.?a)\b", re.I), "bachelors", "Computer Science"),
    (re.compile(r"\b(diploma|associate)\b", re.I), "diploma", "General"),
]

# Stream pattern mapping
_STREAM_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b(computer science|cs|software|it|information technology|data science)\b", re.I), "Computer Science"),
    (re.compile(r"\b(electrical|electronics|ece|ee|hardware)\b", re.I), "Electrical Engineering"),
    (re.compile(r"\b(mechanical|civil|chemical)\b", re.I), "Engineering"),
    (re.compile(r"\b(business|finance|management|mba|economics|marketing)\b", re.I), "Business"),
    (re.compile(r"\b(math|mathematics|statistics|physics)\b", re.I), "Mathematics & Sciences"),
]


def normalize_skill(skill_name: str) -> str:
    """Normalizes a single skill using the OntologyService lookup."""
    return ontology_service.get_canonical_name(skill_name)


def normalize_skills(skills_list: List[Any]) -> List[str]:
    """Extracts and canonicalizes a list of raw skill entries or dicts."""
    normalized = set()
    for item in skills_list:
        val = item.get("value") if isinstance(item, dict) else str(item)
        if val and str(val).strip():
            canonical = normalize_skill(str(val).strip())
            if canonical:
                normalized.add(canonical)
    return sorted(list(normalized))


def normalize_degree(degree_str: str) -> Tuple[str, str]:
    """Parses a degree string to extract (qualification_level, stream)."""
    if not degree_str:
        return "bachelors", "General"

    deg_clean = degree_str.strip()
    qualification = "bachelors"
    stream = "General"

    # Match qualification
    for pattern, qual, default_stream in _DEGREE_PATTERNS:
        if pattern.search(deg_clean):
            qualification = qual
            stream = default_stream
            break

    # Match stream overrides
    for pattern, stream_name in _STREAM_PATTERNS:
        if pattern.search(deg_clean):
            stream = stream_name
            break

    return qualification, stream


def normalize_company(company_str: str) -> str:
    """Cleans legal suffixes and standardizes company names."""
    if not company_str:
        return ""
    cleaned = _COMPANY_SUFFIXES.sub("", company_str)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(",. ")
    return cleaned.title() if cleaned else company_str.strip()


def normalize_institution(institution_str: str) -> str:
    """Cleans and standardizes academic institution names."""
    if not institution_str:
        return ""
    cleaned = re.sub(r"\s+", " ", institution_str).strip(",. ")
    return cleaned.title()


def normalize_entities(parsed_resume: Dict[str, Any]) -> Dict[str, List[str]]:
    """Runs full normalization across all entities in a parsed resume."""
    raw_skills = parsed_resume.get("skills", [])
    raw_frameworks = parsed_resume.get("frameworks", [])
    raw_tools = parsed_resume.get("tools", [])
    raw_languages = parsed_resume.get("languages", [])

    all_tech = raw_skills + raw_frameworks + raw_tools + raw_languages

    companies = [
        normalize_company(exp.get("company", {}).get("value", "") if isinstance(exp.get("company"), dict) else str(exp.get("company", "")))
        for exp in parsed_resume.get("experience", [])
        if exp.get("company")
    ]

    institutions = [
        normalize_institution(edu.get("institution", {}).get("value", "") if isinstance(edu.get("institution"), dict) else str(edu.get("institution", "")))
        for edu in parsed_resume.get("education", [])
        if edu.get("institution")
    ]

    certifications = [
        normalize_skill(cert.get("name", {}).get("value", "") if isinstance(cert.get("name"), dict) else str(cert.get("name", "")))
        for cert in parsed_resume.get("certifications", [])
        if cert.get("name")
    ]

    return {
        "normalized_skills": normalize_skills(raw_skills),
        "normalized_technologies": normalize_skills(all_tech),
        "normalized_companies": sorted(list(set(filter(None, companies)))),
        "normalized_institutions": sorted(list(set(filter(None, institutions)))),
        "normalized_certifications": sorted(list(set(filter(None, certifications)))),
    }

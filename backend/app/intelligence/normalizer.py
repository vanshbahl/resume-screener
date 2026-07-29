"""Deterministic Entity Normalizer for Phase 2.

Normalizes skills, technologies, degrees, education streams, companies, and institutions
without external AI calls. Uses OntologyService and deterministic pattern mapping.
"""

import re
from typing import Any, Dict, List, Tuple

from app.intelligence.ontology_service import ontology_service

# Clean suffix regex for companies
_COMPANY_SUFFIXES = re.compile(
    r"\b(inc|inc\.|llc|ltd|pvt\.|pvt|corp|corporation|co\.|co|gmbh|solutions|technologies|services)\b",
    re.IGNORECASE,
)

# Degree pattern mapping: (regex pattern, qualification, stream)
_DEGREE_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (re.compile(r"\b(ph\.?d|doctor|doctorate)\b", re.I), "phd", "Research"),
    (re.compile(r"\b(m\.?s|master|m\.?tech|m\.?e|m\.?b\.?a)\b", re.I), "masters", "Computer Science"),
    (re.compile(r"\b(b\.?s|bachelor|b\.?tech|b\.?e|b\.?a|b\.?c\.?a)\b", re.I), "bachelors", "Computer Science"),
    (re.compile(r"\b(diploma|associate)\b", re.I), "diploma", "General"),
]

# Stream pattern mapping
_STREAM_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b(computer science|cs|software|it|information technology|data science|artificial intelligence|ai|ml)\b", re.I), "Computer Science"),
    (re.compile(r"\b(electrical|electronics|ece|ee|hardware)\b", re.I), "Electrical Engineering"),
    (re.compile(r"\b(mechanical|civil|chemical)\b", re.I), "Engineering"),
    (re.compile(r"\b(business|finance|management|mba|economics|marketing)\b", re.I), "Business"),
    (re.compile(r"\b(math|mathematics|statistics|physics)\b", re.I), "Mathematics & Sciences"),
]


def _extract_val(item: Any) -> str:
    """Safely extracts text value from ExtractedField dicts or raw strings."""
    if not item:
        return ""
    if isinstance(item, dict):
        val = item.get("value")
        if isinstance(val, str):
            return val.strip()
        if isinstance(val, dict):
            return str(val.get("value", "")).strip()
        return str(val or "").strip()
    return str(item).strip()


def normalize_skill(skill_name: str) -> str:
    """Normalizes a single skill using the OntologyService lookup."""
    clean_name = skill_name.strip()
    if not clean_name:
        return ""
    return ontology_service.get_canonical_name(clean_name)


def normalize_skills(skills_list: List[Any]) -> List[str]:
    """Extracts and canonicalizes a list of raw skill entries, dicts, or strings."""
    normalized = set()
    for item in skills_list:
        val = _extract_val(item)
        if val:
            canonical = normalize_skill(val)
            if canonical:
                normalized.add(canonical)
    return sorted(list(normalized))


def normalize_degree(degree_str: str) -> Tuple[str, str]:
    """Parses a degree string to extract (qualification_level, stream)."""
    if not degree_str:
        return "bachelors", "Computer Science"

    deg_clean = degree_str.strip()
    qualification = "bachelors"
    stream = "Computer Science"

    for pattern, qual, default_stream in _DEGREE_PATTERNS:
        if pattern.search(deg_clean):
            qualification = qual
            stream = default_stream
            break

    for pattern, stream_name in _STREAM_PATTERNS:
        if pattern.search(deg_clean):
            stream = stream_name
            break

    return qualification, stream


def normalize_company(company_str: str) -> str:
    """Cleans legal suffixes and standardizes company names."""
    clean = _extract_val(company_str)
    if not clean:
        return ""
    cleaned = _COMPANY_SUFFIXES.sub("", clean)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(",. ")
    return cleaned.title() if cleaned else clean.title()


def normalize_institution(institution_str: str) -> str:
    """Cleans and standardizes academic institution names."""
    clean = _extract_val(institution_str)
    if not clean:
        return ""
    cleaned = re.sub(r"\s+", " ", clean).strip(",. ")
    return cleaned.title()


def normalize_entities(parsed_resume: Dict[str, Any]) -> Dict[str, List[str]]:
    """Runs full normalization across all entities in a parsed resume."""
    raw_skills = parsed_resume.get("skills", [])
    raw_frameworks = parsed_resume.get("frameworks", [])
    raw_tools = parsed_resume.get("tools", [])
    raw_languages = parsed_resume.get("languages", [])

    # Collect project technologies and experience skills_used
    project_techs: List[Any] = []
    for proj in parsed_resume.get("projects", []):
        if isinstance(proj, dict):
            techs = proj.get("technologies", [])
            if isinstance(techs, list):
                project_techs.extend(techs)

    exp_skills: List[Any] = []
    for exp in parsed_resume.get("experience", []):
        if isinstance(exp, dict):
            used = exp.get("skills_used", [])
            if isinstance(used, list):
                exp_skills.extend(used)

    all_tech = raw_skills + raw_frameworks + raw_tools + raw_languages + project_techs + exp_skills

    companies = [
        normalize_company(exp.get("company"))
        for exp in parsed_resume.get("experience", [])
        if isinstance(exp, dict) and exp.get("company")
    ]

    institutions = [
        normalize_institution(edu.get("institution"))
        for edu in parsed_resume.get("education", [])
        if isinstance(edu, dict) and edu.get("institution")
    ]

    certifications = [
        normalize_skill(_extract_val(cert.get("name") if isinstance(cert, dict) else cert))
        for cert in parsed_resume.get("certifications", [])
        if cert
    ]

    return {
        "normalized_skills": normalize_skills(all_tech),
        "normalized_technologies": normalize_skills(all_tech),
        "normalized_companies": sorted(list(set(filter(None, companies)))),
        "normalized_institutions": sorted(list(set(filter(None, institutions)))),
        "normalized_certifications": sorted(list(set(filter(None, certifications)))),
    }

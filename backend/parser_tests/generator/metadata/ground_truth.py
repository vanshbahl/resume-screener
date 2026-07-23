from typing import Any, Dict


def _wrap_field(value: Any, section: str = None) -> Any:
    """Wraps a primitive value into the parser's expected field-level confidence format."""
    if value is None:
        return None

    # If the value is a list of strings, wrap each string
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return [
            {
                "value": v,
                "confidence": 1.0,
                "source": {"page": 1, "section": section, "line": 0},
                "origin_model": "ground_truth",
            }
            for v in value
        ]

    return {
        "value": value,
        "confidence": 1.0,
        "source": {"page": 1, "section": section, "line": 0},
        "origin_model": "ground_truth",
    }


def generate_expected_json(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Converts a ResumeProfile into the expected parsed JSON output format."""
    pi = profile.get("personal_info", {})

    expected = {
        "personal_info": {
            "name": _wrap_field(pi.get("name"), "personal_info"),
            "email": _wrap_field(pi.get("email"), "personal_info"),
            "phone": _wrap_field(pi.get("phone"), "personal_info"),
            "location": _wrap_field(pi.get("location"), "personal_info"),
            "github": _wrap_field(pi.get("github"), "personal_info"),
            "linkedin": _wrap_field(pi.get("linkedin"), "personal_info"),
            "portfolio": _wrap_field(pi.get("portfolio"), "personal_info"),
            "website": None,
        },
        "summary": _wrap_field(profile.get("summary"), "summary"),
    }

    # Skills
    s = profile.get("skills", {})
    expected["skills"] = _wrap_field(s.get("all", []), "skills")
    expected["languages"] = _wrap_field(s.get("languages", []), "skills")
    expected["frameworks"] = _wrap_field(s.get("frameworks", []), "skills")
    expected["tools"] = _wrap_field(s.get("tools", []), "skills")
    expected["concepts"] = []
    expected["soft_skills"] = []
    expected["spoken_languages"] = []

    # Experience
    exp_list = []
    for exp in profile.get("experience", []):
        exp_list.append(
            {
                "company": _wrap_field(exp["company"], "experience"),
                "title": _wrap_field(exp["title"], "experience"),
                "start_date": _wrap_field(exp["start_date"], "experience"),
                "end_date": _wrap_field(exp["end_date"], "experience"),
                "responsibilities": _wrap_field(
                    exp.get("responsibilities", []), "experience"
                ),
            }
        )
    expected["experience"] = exp_list

    # Projects
    proj_list = []
    for proj in profile.get("projects", []):
        proj_list.append(
            {
                "name": _wrap_field(proj["name"], "projects"),
                "description": _wrap_field(proj["description"], "projects"),
                "link": _wrap_field(proj.get("link"), "projects"),
                "technologies": _wrap_field(proj.get("technologies", []), "projects"),
            }
        )
    expected["projects"] = proj_list

    # Education
    edu_list = []
    for edu in profile.get("education", []):
        edu_list.append(
            {
                "institution": _wrap_field(edu["institution"], "education"),
                "degree": _wrap_field(edu["degree"], "education"),
                "graduation_year": _wrap_field(edu["graduation_year"], "education"),
                "cgpa": _wrap_field(edu.get("cgpa"), "education"),
            }
        )
    expected["education"] = edu_list

    expected["metadata"] = {
        "parsing_confidence": 1.0,
        "entities_detected": 100,
        "sections_detected": [
            "personal_info",
            "experience",
            "projects",
            "education",
            "skills",
        ],
        "parsing_time_ms": 0,
        "entities_added_by_ai": 0,
    }

    return expected


def generate_metadata_json(profile: Dict[str, Any]) -> Dict[str, Any]:
    meta = profile.get("metadata", {})
    return {
        "experience_level": meta.get("experience_level"),
        "industry": meta.get("industry"),
        "country": meta.get("country"),
        "has_summary": meta.get("has_summary"),
        "has_projects": meta.get("has_projects"),
        "has_experience": meta.get("has_experience"),
        "difficulty": "Medium",  # Default for now
    }


def generate_notes_md(profile: Dict[str, Any]) -> str:
    meta = profile.get("metadata", {})
    notes = [
        "# Dataset Notes",
        "",
        "This resume tests:",
        f"- Industry: {meta.get('industry')}",
        f"- Experience Level: {meta.get('experience_level')}",
        f"- Country Format: {meta.get('country')}",
    ]
    if not meta.get("has_summary"):
        notes.append("- No summary block")
    if not meta.get("has_projects"):
        notes.append("- No projects section")
    if not meta.get("has_experience"):
        notes.append("- No experience section (Fresher layout)")

    return "\n".join(notes)

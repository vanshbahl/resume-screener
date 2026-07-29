"""AI Evaluator for Phase 2.

Performs qualitative reasoning (domain classification, target role inference, project complexity evaluation,
career trajectory analysis, and strength/weakness summarization).
Includes lightweight offline NLP fallbacks to operate without external LLM dependencies.
"""

from typing import Any, Dict, List
from app.intelligence.models import ProjectDetail


def _extract_val(field: Any) -> str:
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


def _infer_domains(normalized_skills: List[str]) -> tuple[str, List[str], List[str]]:
    """Infers primary domain, secondary domains, and target roles based on skill clusters."""
    skills_set = {s.lower() for s in normalized_skills}

    backend_keywords = {"python", "fastapi", "django", "postgresql", "node", "java", "golang", "rest api", "sql", "docker", "microservices", "api"}
    frontend_keywords = {"react", "typescript", "javascript", "html", "css", "vue", "next.js", "tailwind", "redux"}
    data_keywords = {"python", "pandas", "numpy", "machine learning", "pytorch", "tensorflow", "scikit-learn", "sql", "spark"}
    cloud_keywords = {"aws", "kubernetes", "docker", "terraform", "ci/cd", "linux", "cloud", "ansible"}

    backend_match = len(skills_set.intersection(backend_keywords))
    frontend_match = len(skills_set.intersection(frontend_keywords))
    data_match = len(skills_set.intersection(data_keywords))
    cloud_match = len(skills_set.intersection(cloud_keywords))

    scores = [
        ("Backend Engineering", backend_match, ["Backend Developer", "Software Engineer", "API Engineer"]),
        ("Frontend Engineering", frontend_match, ["Frontend Developer", "UI/UX Engineer", "Web Developer"]),
        ("Data Science & ML", data_match, ["Data Scientist", "ML Engineer", "Data Analyst"]),
        ("DevOps & Cloud Infrastructure", cloud_match, ["DevOps Engineer", "Cloud Architect", "SRE"]),
    ]

    scores.sort(key=lambda x: x[1], reverse=True)

    if scores[0][1] == 0:
        return "General Software Engineering", ["Software Development"], ["Software Engineer"]

    primary = scores[0][0]
    target_roles = scores[0][2]

    if backend_match > 0 and frontend_match > 0:
        primary = "Full-Stack Engineering"
        target_roles = ["Full-Stack Developer", "Software Engineer"]

    secondary = [s[0] for s in scores[1:] if s[1] > 0]

    return primary, secondary, target_roles


def _evaluate_project(proj: Dict[str, Any]) -> ProjectDetail:
    """Evaluates technical depth, scale, complexity, and tech stack maturity of a project."""
    name = _extract_val(proj.get("name")) or "Untitled Project"
    desc = _extract_val(proj.get("description"))

    # Also collect technologies list if present
    tech_list: List[str] = []
    raw_techs = proj.get("technologies", [])
    if isinstance(raw_techs, list):
        for t in raw_techs:
            v = _extract_val(t)
            if v:
                tech_list.append(v)

    combined_text = f"{desc} {' '.join(tech_list)}".lower()

    # Complexity heuristic
    complexity = "Medium"
    if any(k in combined_text for k in ["microservices", "distributed", "kubernetes", "real-time", "kafka", "high-scale", "enterprise", "vector"]):
        complexity = "Enterprise"
    elif any(k in combined_text for k in ["pipeline", "api", "database", "authentication", "docker", "fastapi", "react", "postgresql"]):
        complexity = "High"
    elif len(combined_text) < 15:
        complexity = "Low"

    # Scale heuristic
    scale = "Medium"
    if any(k in combined_text for k in ["thousand", "million", "cluster", "distributed", "large scale", "high concurrency"]):
        scale = "Large Scale"
    elif any(k in combined_text for k in ["api", "database", "service"]):
        scale = "Medium"
    else:
        scale = "Small"

    # Modernity heuristic
    modernity = "Modern"
    if any(k in combined_text for k in ["fastapi", "react", "next.js", "pytorch", "transformers", "vector", "typescript"]):
        modernity = "Cutting-Edge"
    elif any(k in combined_text for k in ["jquery", "cobol", "php 5", "asp.net"]):
        modernity = "Legacy"

    return ProjectDetail(
        name=name,
        complexity=complexity,
        technical_depth=f"Built using: {', '.join(tech_list)}" if tech_list else (desc[:80] or "Technical details provided."),
        business_impact="Demonstrated implementation of core functionality." if desc else None,
        scale=scale,
        modernity=modernity,
        tech_stack_maturity="Production-Grade" if complexity in ("High", "Enterprise") else "Intermediate",
    )


def evaluate_qualitative_profile(
    parsed_resume: Dict[str, Any],
    normalized_skills: List[str],
    total_yoe: float,
) -> Dict[str, Any]:
    """Runs qualitative AI reasoning over the parsed profile."""
    primary_domain, secondary_domains, target_roles = _infer_domains(normalized_skills)

    # Career stage determination
    if total_yoe < 2.0:
        career_stage = "Entry-level"
        seniority = "Junior"
    elif total_yoe < 5.0:
        career_stage = "Mid-level"
        seniority = "Mid-Level"
    elif total_yoe < 8.0:
        career_stage = "Senior"
        seniority = "Senior"
    else:
        career_stage = "Lead"
        seniority = "Lead / Principal"

    # Projects evaluation
    raw_projects = parsed_resume.get("projects", [])
    evaluated_projects = [_evaluate_project(p) for p in raw_projects if isinstance(p, dict)]

    # Strengths & Weaknesses
    strengths = []
    weaknesses = []

    if len(normalized_skills) >= 6:
        strengths.append(f"Broad technical skill set across {len(normalized_skills)} technologies.")
    if total_yoe >= 1.0:
        strengths.append(f"Industry work experience with {total_yoe} years of tenure.")
    if len(evaluated_projects) >= 2:
        strengths.append(f"Demonstrated hands-on experience through {len(evaluated_projects)} documented projects.")

    if len(normalized_skills) < 4:
        weaknesses.append("Narrow technical skill portfolio.")
    if total_yoe < 1.0:
        weaknesses.append("Limited commercial work experience.")

    return {
        "primary_domain": primary_domain,
        "secondary_domains": secondary_domains,
        "career_stage": career_stage,
        "current_experience_level": seniority,
        "target_roles": target_roles,
        "industry": "Technology & Software",
        "seniority": seniority,
        "technical_specialization": f"{primary_domain} Specialist" if len(normalized_skills) >= 5 else "Generalist",
        "projects": evaluated_projects,
        "strengths": strengths if strengths else ["Clear resume structure"],
        "weaknesses": weaknesses if weaknesses else ["Room to highlight more quantitative project impacts"],
    }

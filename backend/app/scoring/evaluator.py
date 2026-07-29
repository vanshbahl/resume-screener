"""Declarative Rule Evaluator for Phase 3.

Evaluates a CandidateProfile against declarative rules defined in scoring_rules.yaml.
Produces traceable ScoreTraceItems and raw section scores.
"""

from typing import Any, Dict, List, Tuple

from app.intelligence.models import CandidateProfile
from app.scoring.models import ScoreDeltaType, ScoreTraceItem, SectionScore, ScoringCategory


def evaluate_contact_structure(
    profile: CandidateProfile, rules: Dict[str, Any], weight: float
) -> SectionScore:
    """Evaluates contact info and profile links structure."""
    traces: List[ScoreTraceItem] = []
    raw_points = 0.0

    # Detected gaps check
    gap_types = {g.gap_type for g in profile.detected_gaps}

    contact_rules = rules.get("contact_structure", [])
    for rule in contact_rules:
        r_id = rule["rule_id"]
        pts = float(rule["points"])
        desc = rule["description"]

        if r_id == "RULE_CONTACT_EMAIL" and "missing_contact" not in gap_types:
            raw_points += pts
            traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.CONTACT_STRUCTURE, delta_type=ScoreDeltaType.BONUS, points=pts, reason=desc))
        elif r_id == "RULE_CONTACT_PHONE" and "missing_contact" not in gap_types:
            raw_points += pts
            traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.CONTACT_STRUCTURE, delta_type=ScoreDeltaType.BONUS, points=pts, reason=desc))
        elif r_id == "RULE_CONTACT_LINKEDIN" and not any(g.gap_type == "missing_link" and "LinkedIn" in g.description for g in profile.detected_gaps):
            raw_points += pts
            traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.CONTACT_STRUCTURE, delta_type=ScoreDeltaType.BONUS, points=pts, reason=desc))
        elif r_id == "RULE_CONTACT_GITHUB" and not any(g.gap_type == "missing_link" and "GitHub" in g.description for g in profile.detected_gaps):
            raw_points += pts
            traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.CONTACT_STRUCTURE, delta_type=ScoreDeltaType.BONUS, points=pts, reason=desc))

    raw_score = min(100.0, max(0.0, raw_points))
    return SectionScore(
        category=ScoringCategory.CONTACT_STRUCTURE,
        raw_score=raw_score,
        weight=weight,
        weighted_score=round(raw_score * weight, 2),
        traces=traces,
    )


def evaluate_education(
    profile: CandidateProfile, rules: Dict[str, Any], weight: float
) -> SectionScore:
    """Evaluates highest qualification and degree status."""
    traces: List[ScoreTraceItem] = []
    raw_points = 0.0

    edu_cfg = rules.get("education", {})
    quals = edu_cfg.get("qualifications", {})
    highest_qual = profile.education_summary.highest_qualification.lower()

    qual_meta = quals.get(highest_qual) or quals.get("bachelors", {"points": 80.0, "rule_id": "RULE_EDU_QUAL_BACHELORS", "description": "Bachelor's degree"})
    pts = float(qual_meta["points"])
    r_id = qual_meta["rule_id"]
    desc = qual_meta["description"]

    raw_points += pts
    traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.EDUCATION, delta_type=ScoreDeltaType.BONUS, points=pts, reason=desc))

    if profile.education_summary.graduation_status.lower() == "completed":
        for b in edu_cfg.get("bonuses", []):
            if b["rule_id"] == "RULE_EDU_STATUS_COMPLETED":
                b_pts = float(b["points"])
                raw_points += b_pts
                traces.append(ScoreTraceItem(rule_id=b["rule_id"], category=ScoringCategory.EDUCATION, delta_type=ScoreDeltaType.BONUS, points=b_pts, reason=b["description"]))

    raw_score = min(100.0, max(0.0, raw_points))
    return SectionScore(
        category=ScoringCategory.EDUCATION,
        raw_score=raw_score,
        weight=weight,
        weighted_score=round(raw_score * weight, 2),
        traces=traces,
    )


def evaluate_experience(
    profile: CandidateProfile, rules: Dict[str, Any], weight: float
) -> SectionScore:
    """Evaluates tenure, growth trajectory, and employment gaps."""
    traces: List[ScoreTraceItem] = []
    raw_points = 0.0

    exp_cfg = rules.get("experience", {})
    yoe = profile.experience_summary.total_years_experience
    mult = float(exp_cfg.get("yoe_base_multiplier", 15.0))
    cap = float(exp_cfg.get("yoe_cap", 80.0))
    r_id_yoe = exp_cfg.get("yoe_rule_id", "RULE_EXP_TENURE")

    yoe_pts = min(cap, round(yoe * mult, 1))
    if yoe_pts > 0:
        raw_points += yoe_pts
        traces.append(ScoreTraceItem(rule_id=r_id_yoe, category=ScoringCategory.EXPERIENCE, delta_type=ScoreDeltaType.BONUS, points=yoe_pts, reason=f"Earned {yoe_pts} points for {yoe} YOE"))

    trajectory = profile.experience_summary.growth_trajectory
    traj_cfg = exp_cfg.get("trajectory_bonuses", {}).get(trajectory)
    if traj_cfg:
        t_pts = float(traj_cfg["points"])
        raw_points += t_pts
        traces.append(ScoreTraceItem(rule_id=traj_cfg["rule_id"], category=ScoringCategory.EXPERIENCE, delta_type=ScoreDeltaType.BONUS, points=t_pts, reason=traj_cfg["description"]))

    # Check gap penalties
    has_gap = any(g.gap_type == "employment_gap" for g in profile.detected_gaps)
    if has_gap:
        for pen in exp_cfg.get("penalties", []):
            if pen["rule_id"] == "RULE_EXP_EMPLOYMENT_GAP":
                p_pts = float(pen["points"])
                raw_points += p_pts  # Negative value
                traces.append(ScoreTraceItem(rule_id=pen["rule_id"], category=ScoringCategory.EXPERIENCE, delta_type=ScoreDeltaType.DEDUCTION, points=p_pts, reason=pen["description"]))

    raw_score = min(100.0, max(0.0, raw_points))
    return SectionScore(
        category=ScoringCategory.EXPERIENCE,
        raw_score=raw_score,
        weight=weight,
        weighted_score=round(raw_score * weight, 2),
        traces=traces,
    )


def evaluate_projects(
    profile: CandidateProfile, rules: Dict[str, Any], weight: float
) -> SectionScore:
    """Evaluates project count and complexity bonuses."""
    traces: List[ScoreTraceItem] = []
    raw_points = 0.0

    proj_cfg = rules.get("projects", {})
    per_proj = float(proj_cfg.get("points_per_project", 25.0))
    cap = float(proj_cfg.get("project_cap", 70.0))
    r_id = proj_cfg.get("project_rule_id", "RULE_PROJ_VOLUME")

    vol_pts = min(cap, len(profile.projects) * per_proj)
    if vol_pts > 0:
        raw_points += vol_pts
        traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.PROJECTS, delta_type=ScoreDeltaType.BONUS, points=vol_pts, reason=f"Showcased {len(profile.projects)} projects"))

    comp_cfg = proj_cfg.get("complexity_bonuses", {})
    for proj in profile.projects:
        c_meta = comp_cfg.get(proj.complexity)
        if c_meta:
            c_pts = float(c_meta["points"])
            raw_points += c_pts
            traces.append(ScoreTraceItem(rule_id=c_meta["rule_id"], category=ScoringCategory.PROJECTS, delta_type=ScoreDeltaType.BONUS, points=c_pts, reason=f"Project '{proj.name}': {c_meta['description']}"))

    raw_score = min(100.0, max(0.0, raw_points))
    return SectionScore(
        category=ScoringCategory.PROJECTS,
        raw_score=raw_score,
        weight=weight,
        weighted_score=round(raw_score * weight, 2),
        traces=traces,
    )


def evaluate_skills(
    profile: CandidateProfile, rules: Dict[str, Any], weight: float
) -> SectionScore:
    """Evaluates skill portfolio and certifications."""
    traces: List[ScoreTraceItem] = []
    raw_points = 0.0

    skill_cfg = rules.get("skills", {})
    per_skill = float(skill_cfg.get("points_per_skill", 5.0))
    cap = float(skill_cfg.get("skills_cap", 80.0))
    r_id = skill_cfg.get("skill_rule_id", "RULE_SKILL_PORTFOLIO")

    sk_pts = min(cap, len(profile.normalized_skills) * per_skill)
    if sk_pts > 0:
        raw_points += sk_pts
        traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.SKILLS, delta_type=ScoreDeltaType.BONUS, points=sk_pts, reason=f"Extracted {len(profile.normalized_skills)} normalized skills"))

    cert_pts_item = float(skill_cfg.get("certification_bonus_per_item", 10.0))
    cert_cap = float(skill_cfg.get("certification_cap", 20.0))
    cert_r_id = skill_cfg.get("certification_rule_id", "RULE_SKILL_CERTIFICATION_BONUS")

    c_pts = min(cert_cap, len(profile.normalized_certifications) * cert_pts_item)
    if c_pts > 0:
        raw_points += c_pts
        traces.append(ScoreTraceItem(rule_id=cert_r_id, category=ScoringCategory.SKILLS, delta_type=ScoreDeltaType.BONUS, points=c_pts, reason=f"Earned certification bonus for {len(profile.normalized_certifications)} certs"))

    raw_score = min(100.0, max(0.0, raw_points))
    return SectionScore(
        category=ScoringCategory.SKILLS,
        raw_score=raw_score,
        weight=weight,
        weighted_score=round(raw_score * weight, 2),
        traces=traces,
    )


def evaluate_writing_quality(
    profile: CandidateProfile, rules: Dict[str, Any], weight: float
) -> SectionScore:
    """Evaluates quantifiable metrics, gap cleanliness, and project descriptions."""
    traces: List[ScoreTraceItem] = []
    raw_points = 0.0

    wq_cfg = rules.get("writing_quality", {})

    has_missing_metrics = any(g.gap_type == "missing_metrics" for g in profile.detected_gaps)
    if not has_missing_metrics:
        pts = float(wq_cfg.get("metrics_present_bonus", 40.0))
        r_id = wq_cfg.get("metrics_rule_id", "RULE_QUALITY_METRICS_PRESENT")
        raw_points += pts
        traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.WRITING_QUALITY, delta_type=ScoreDeltaType.BONUS, points=pts, reason="Includes quantifiable metrics (%, $, numbers) in work experience"))

    critical_gaps = [g for g in profile.detected_gaps if g.severity == "critical"]
    if not critical_gaps:
        pts = float(wq_cfg.get("no_critical_gaps_bonus", 30.0))
        r_id = wq_cfg.get("no_gaps_rule_id", "RULE_QUALITY_NO_CRITICAL_GAPS")
        raw_points += pts
        traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.WRITING_QUALITY, delta_type=ScoreDeltaType.BONUS, points=pts, reason="Zero critical structure or contact gaps identified"))

    thin_proj_descs = any(g.gap_type == "missing_project_description" for g in profile.detected_gaps)
    if not thin_proj_descs and profile.projects:
        pts = float(wq_cfg.get("project_descriptions_bonus", 30.0))
        r_id = wq_cfg.get("project_desc_rule_id", "RULE_QUALITY_PROJECT_DESCRIPTIONS")
        raw_points += pts
        traces.append(ScoreTraceItem(rule_id=r_id, category=ScoringCategory.WRITING_QUALITY, delta_type=ScoreDeltaType.BONUS, points=pts, reason="Detailed technical descriptions provided across portfolio projects"))

    raw_score = min(100.0, max(0.0, raw_points))
    return SectionScore(
        category=ScoringCategory.WRITING_QUALITY,
        raw_score=raw_score,
        weight=weight,
        weighted_score=round(raw_score * weight, 2),
        traces=traces,
    )


def evaluate_all_sections(
    profile: CandidateProfile, rules_config: Dict[str, Any]
) -> Tuple[Dict[str, SectionScore], List[ScoreTraceItem]]:
    """Runs all declarative rule calculators and aggregates section scores and traces."""
    scoring = rules_config.get("scoring", {})
    weights = scoring.get("weights", {})
    rules = scoring.get("rules", {})

    section_scores: Dict[str, SectionScore] = {}
    all_traces: List[ScoreTraceItem] = []

    calculators = [
        ("contact_structure", evaluate_contact_structure),
        ("education", evaluate_education),
        ("experience", evaluate_experience),
        ("projects", evaluate_projects),
        ("skills", evaluate_skills),
        ("writing_quality", evaluate_writing_quality),
    ]

    for key, calc_fn in calculators:
        w = float(weights.get(key, 0.15))
        sec_score = calc_fn(profile, rules, w)
        section_scores[key] = sec_score
        all_traces.extend(sec_score.traces)

    return section_scores, all_traces

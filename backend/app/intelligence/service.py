"""Resume Intelligence Service for Phase 2.

Orchestrates entity normalization, experience/education analysis, gap detection,
and qualitative AI evaluation to generate a canonical CandidateProfile.
"""

from typing import Any, Dict, Optional

from app.intelligence.analyzer import analyze_education, analyze_experience, detect_gaps
from app.intelligence.evaluator import evaluate_qualitative_profile
from app.intelligence.models import CandidateProfile
from app.intelligence.normalizer import normalize_entities


class ResumeIntelligenceService:
    """Service responsible for generating a CandidateProfile from parsed resume data."""

    def generate_profile(
        self,
        candidate_id: str,
        resume_id: str,
        parsed_metadata: Dict[str, Any],
        resume_analysis: Optional[Dict[str, Any]] = None,
    ) -> CandidateProfile:
        """Transforms raw parsed resume metadata and completeness analysis into a canonical CandidateProfile."""
        if not parsed_metadata:
            parsed_metadata = {}

        # 1. Deterministic Normalization
        norm = normalize_entities(parsed_metadata)

        # 2. Deterministic Analysis
        exp_summary = analyze_experience(parsed_metadata)
        edu_summary = analyze_education(parsed_metadata)
        gaps = detect_gaps(parsed_metadata)

        # 3. Qualitative AI Reasoning
        qual = evaluate_qualitative_profile(
            parsed_resume=parsed_metadata,
            normalized_skills=norm["normalized_skills"],
            total_yoe=exp_summary.total_years_experience,
        )

        # 4. Construct Canonical CandidateProfile
        profile = CandidateProfile(
            candidate_id=candidate_id,
            resume_id=resume_id,
            primary_domain=qual["primary_domain"],
            secondary_domains=qual["secondary_domains"],
            career_stage=qual["career_stage"],
            education_stream=edu_summary.education_stream,
            current_experience_level=qual["current_experience_level"],
            target_roles=qual["target_roles"],
            industry=qual["industry"],
            seniority=qual["seniority"],
            technical_specialization=qual["technical_specialization"],
            normalized_skills=norm["normalized_skills"],
            normalized_technologies=norm["normalized_technologies"],
            normalized_companies=norm["normalized_companies"],
            normalized_institutions=norm["normalized_institutions"],
            normalized_certifications=norm["normalized_certifications"],
            projects=qual["projects"],
            experience_summary=exp_summary,
            education_summary=edu_summary,
            strengths=qual["strengths"],
            weaknesses=qual["weaknesses"],
            detected_gaps=gaps,
            raw_parsed_summary={
                "skills_count": len(norm["normalized_skills"]),
                "projects_count": len(qual["projects"]),
                "yoe": exp_summary.total_years_experience,
            },
        )

        return profile


# Singleton instance
resume_intelligence_service = ResumeIntelligenceService()

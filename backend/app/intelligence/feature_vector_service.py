from typing import Any, Dict, List

from app.intelligence.ontology_service import ontology_service
from app.schemas.intelligence import FeatureVector


class FeatureVectorService:
    def __init__(self):
        self.ontology = ontology_service

    def _extract_normalized_list(self, raw_list: List[Dict[str, Any]]) -> List[str]:
        """Extracts 'value' from parsed entity dictionaries and canonicalizes them."""
        normalized = set()
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            val = item.get("value")
            if val:
                canonical = self.ontology.get_canonical_name(val)
                normalized.add(canonical)
        return list(normalized)

    def _extract_years_experience(self, experience_list: List[Dict[str, Any]]) -> float:
        """Calculates total years of experience from a list of parsed Experience entries."""
        total_months = 0
        for exp in experience_list:
            # Assuming duration_months is populated in the parsed output, or fallback to rough estimates
            duration = exp.get("duration_months")
            if duration:
                total_months += float(duration)
        return round(total_months / 12, 1)

    def _extract_education_level(self, education_list: List[Dict[str, Any]]) -> str:
        """Determines highest education level from parsed entries."""
        levels = {"high_school": 1, "bachelors": 2, "masters": 3, "phd": 4}
        highest = "none"
        highest_score = 0

        for ed in education_list:
            deg = str(ed.get("degree", "")).lower()
            if "phd" in deg or "doctor" in deg:
                score = 4
                lvl = "phd"
            elif "master" in deg or "ms" in deg or "mba" in deg:
                score = 3
                lvl = "masters"
            elif "bachelor" in deg or "bs" in deg or "ba" in deg or "b.tech" in deg:
                score = 2
                lvl = "bachelors"
            else:
                score = 1
                lvl = "high_school"

            if score > highest_score:
                highest_score = score
                highest = lvl

        return highest

    def convert_resume_to_vector(self, parsed_resume: Dict[str, Any]) -> FeatureVector:
        """Converts a parsed resume dictionary into a standardized FeatureVector."""
        return FeatureVector(
            skills=self._extract_normalized_list(parsed_resume.get("skills", [])),
            frameworks=self._extract_normalized_list(
                parsed_resume.get("frameworks", [])
            ),
            tools=self._extract_normalized_list(parsed_resume.get("tools", [])),
            concepts=self._extract_normalized_list(parsed_resume.get("concepts", [])),
            languages=self._extract_normalized_list(parsed_resume.get("languages", [])),
            databases=self._extract_normalized_list(parsed_resume.get("databases", [])),
            cloud=self._extract_normalized_list(parsed_resume.get("cloud", [])),
            soft_skills=self._extract_normalized_list(
                parsed_resume.get("soft_skills", [])
            ),
            years_experience=self._extract_years_experience(
                parsed_resume.get("experience", [])
            ),
            education_level=self._extract_education_level(
                parsed_resume.get("education", [])
            ),
            certifications=self._extract_normalized_list(
                parsed_resume.get("certifications", [])
            ),
            # Additional heuristics can be applied here
            leadership_score=1.0 if "lead" in str(parsed_resume).lower() else 0.0,
            project_complexity_score=float(len(parsed_resume.get("projects", [])))
            * 0.5,
            technology_focus=(
                "specialist"
                if len(parsed_resume.get("skills", [])) < 5
                else "generalist"
            ),
        )

    def convert_job_to_vectors(
        self, parsed_job: Dict[str, Any]
    ) -> tuple[FeatureVector, FeatureVector]:
        """Converts a parsed JD into a required and preferred FeatureVector."""
        req = FeatureVector(
            skills=self._extract_normalized_list(parsed_job.get("required_skills", [])),
            frameworks=self._extract_normalized_list(parsed_job.get("frameworks", [])),
            tools=self._extract_normalized_list(parsed_job.get("tools", [])),
            concepts=self._extract_normalized_list(parsed_job.get("concepts", [])),
            languages=self._extract_normalized_list(parsed_job.get("languages", [])),
            soft_skills=self._extract_normalized_list(
                parsed_job.get("soft_skills", [])
            ),
            # Simple heuristic: JD experience usually comes as a single field
            years_experience=float(
                parsed_job.get("experience_requirements", 0.0) or 0.0
            ),
            education_level="bachelors",  # Fallback heuristic
        )
        pref = FeatureVector(
            skills=self._extract_normalized_list(parsed_job.get("preferred_skills", []))
        )
        return req, pref


# Singleton instance
feature_vector_service = FeatureVectorService()

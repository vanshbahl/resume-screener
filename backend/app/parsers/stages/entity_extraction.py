import re
from typing import List, Dict, Optional, Any
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import ResumeDocument, PipelineContext

from app.ai.extractors.contact_extractor import ContactExtractor
from app.ai.extractors.skills_extractor import SkillsExtractor
from app.ai.extractors.experience_extractor import ExperienceExtractor
from app.ai.extractors.project_extractor import ProjectExtractor
from app.ai.extractors.education_extractor import EducationExtractor
from app.ai.extractors.achievement_extractor import AchievementExtractor
from app.ai.extractors.certification_extractor import CertificationExtractor
from app.ai.extractors.language_extractor import LanguageExtractor


class EntityExtractionStage(BaseParserStage):
    def __init__(self):
        super().__init__()
        self.contact_extractor = ContactExtractor()
        self.skills_extractor = SkillsExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.project_extractor = ProjectExtractor()
        self.education_extractor = EducationExtractor()
        self.achievement_extractor = AchievementExtractor()
        self.certification_extractor = CertificationExtractor()
        self.language_extractor = LanguageExtractor()

    def run(self, document: ResumeDocument, context: PipelineContext) -> None:
        pi_lines = document.sections.get("personal_info", {}).get("lines", [])
        if not pi_lines and len(document.raw_lines) > 0:
            pi_lines = document.raw_lines[:15] # Fallback to first 15 lines
            
        contacts = self.contact_extractor.extract(pi_lines)
        
        # Fallback: If critical contact fields are still missing, scan all cleaned_lines.
        # Some PDFs render contacts after a section header (e.g., after Education), so
        # they never land in the personal_info section.
        missing_critical = not contacts.get("email") or not contacts.get("phone")
        if missing_critical:
            full_contacts = self.contact_extractor.extract(document.cleaned_lines)
            for field in ["email", "phone", "linkedin", "github", "portfolio", "location"]:
                if not contacts.get(field) and full_contacts.get(field):
                    contacts[field] = full_contacts[field]
        skills_dict = self.skills_extractor.extract(document.sections.get("skills", {}).get("lines", []), context)
        
        # ROOT CAUSE #4 FIX: Also scan experience and project lines for skills mentioned in bullet points.
        # Many resumes list technologies inline in job descriptions, not just in the skills section.
        # NOTE: Deduplication uses a global set for the flat `skills` pool only.
        #       Each category (languages, frameworks, concepts…) deduplicates independently.
        flat_skill_values = {s["value"] for s in skills_dict.get("skills", [])}
        for section_key in ["experience", "projects"]:
            section_lines = document.sections.get(section_key, {}).get("lines", [])
            if section_lines:
                extra = self.skills_extractor.extract(section_lines, context)
                # Update each category independently
                for cat in ["languages", "frameworks", "tools", "concepts", "soft_skills"]:
                    existing_in_cat = {s["value"] for s in skills_dict.get(cat, [])}
                    for item in extra.get(cat, []):
                        if item["value"] not in existing_in_cat:
                            skills_dict[cat].append(item)
                            existing_in_cat.add(item["value"])
                # Separately update the flat skills pool (union of all categories)
                for item in extra.get("skills", []):
                    if item["value"] not in flat_skill_values:
                        skills_dict["skills"].append(item)
                        flat_skill_values.add(item["value"])
        
        extracted = {
            "personal_info": contacts,
            "summary": None,
            "skills": skills_dict.get("skills", []),
            "languages": skills_dict.get("languages", []),
            "spoken_languages": self.language_extractor.extract(document.sections.get("languages", {}).get("lines", []) or document.sections.get("skills", {}).get("lines", [])),
            "frameworks": skills_dict.get("frameworks", []),
            "tools": skills_dict.get("tools", []),
            "concepts": skills_dict.get("concepts", []),
            "soft_skills": skills_dict.get("soft_skills", []),
            "education": self.education_extractor.extract(document.sections.get("education", {}).get("lines", []), context),
            "experience": self.experience_extractor.extract(document.sections.get("experience", {}).get("lines", []), context),
            "projects": self.project_extractor.extract(document.sections.get("projects", {}).get("lines", []), context),
            "certifications": self.certification_extractor.extract(document.sections.get("certifications", {}).get("lines", [])),
            "achievements": self.achievement_extractor.extract(document.sections.get("achievements", {}).get("lines", []))
        }
        
        summary_lines = document.sections.get("summary", {}).get("lines", [])
        if summary_lines:
            desc = "\n".join(x["text"] for x in summary_lines)
            extracted["summary"] = {
                "value": desc,
                "confidence": 0.9,
                "source": {
                    "page": summary_lines[0]["page"],
                    "section": "summary",
                    "line": summary_lines[0]["line_no"]
                },
                "origin_model": "deterministic"
            }
            
        document.extracted_entities = extracted

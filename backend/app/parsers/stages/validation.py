from datetime import datetime

from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import (BaseDocument, JobDocument,
                                       PipelineContext)
from app.parsers.job_validator import validate_and_score_jd
from app.parsers.resume_validator import validate_and_score


class ValidationStage(BaseParserStage):
    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        if isinstance(document, JobDocument):
            self._validate_jd(document, context)
        else:
            self._validate_resume(document, context)

    def _validate_jd(self, document: JobDocument, context: PipelineContext) -> None:
        extracted = document.normalized_entities

        raw_dict = {
            "job_metadata": extracted.get("job_metadata", {}),
            "salary": extracted.get("salary"),
            "employment_type": extracted.get("employment_type"),
            "location": extracted.get("location_type"),
            "experience_requirements": extracted.get("experience_requirements"),
            "education_requirements": extracted.get("education_requirements", []),
            "visa_requirements": extracted.get("visa_requirements", []),
            "required_skills": extracted.get("required_skills", []),
            "preferred_skills": extracted.get("preferred_skills", []),
            "responsibilities": extracted.get("responsibilities", []),
            "qualifications": extracted.get("qualifications", []),
            "technologies": extracted.get("technologies", []),
            "soft_skills": extracted.get("soft_skills", []),
            "tools": extracted.get("tools", []),
            "frameworks": extracted.get("frameworks", []),
            "concepts": extracted.get("concepts", []),
            "languages": extracted.get("languages", []),
            "certifications": extracted.get("certifications", []),
            "benefits": extracted.get("benefits", []),
            "keywords": extracted.get("keywords", []),
            "raw_data": {"sections": document.sections},
            "metadata": {
                "parser_version": "1.3.0",
                "schema_version": "1.0.0",
                "parsed_at": datetime.utcnow().isoformat() + "Z",
                "processing_time_ms": 0,
                "ai_inference_time_ms": document.metadata.get(
                    "ai_inference_time_ms", 0
                ),
                "page_count": document.metadata.get("page_count", 0),
                "word_count": document.metadata.get("word_count", 0),
                "sections_detected": list(document.sections.keys()),
                "entities_detected": 0,
                "entities_added_by_ai": document.metadata.get(
                    "entities_added_by_ai", 0
                ),
                "entities_modified_by_ai": document.metadata.get(
                    "entities_modified_by_ai", 0
                ),
                "parsing_confidence": 0.0,
                "model_versions": document.metadata.get("model_versions", {}),
                "job_id": getattr(document, "job_id", None),
            },
        }

        document.final_json = validate_and_score_jd(raw_dict)
        document.validation_results = True

    def _validate_resume(
        self, document: BaseDocument, context: PipelineContext
    ) -> None:
        extracted = document.normalized_entities

        raw_dict = {
            "personal_info": extracted.get("personal_info", {}),
            "summary": extracted.get("summary"),
            "skills": extracted.get("skills", []),
            "languages": extracted.get("languages", []),
            "spoken_languages": extracted.get("spoken_languages", []),
            "frameworks": extracted.get("frameworks", []),
            "tools": extracted.get("tools", []),
            "concepts": extracted.get("concepts", []),
            "soft_skills": extracted.get("soft_skills", []),
            "education": extracted.get("education", []),
            "experience": extracted.get("experience", []),
            "projects": extracted.get("projects", []),
            "certifications": extracted.get("certifications", []),
            "achievements": extracted.get("achievements", []),
            "raw_data": {"sections": document.sections},
            "metadata": {
                "parser_version": "1.3.0",
                "schema_version": "1.0.0",
                "parsed_at": datetime.utcnow().isoformat() + "Z",
                "processing_time_ms": 0,
                "ai_inference_time_ms": document.metadata.get(
                    "ai_inference_time_ms", 0
                ),
                "page_count": document.metadata.get("page_count", 0),
                "word_count": document.metadata.get("word_count", 0),
                "sections_detected": list(document.sections.keys()),
                "entities_detected": 0,
                "entities_added_by_ai": document.metadata.get(
                    "entities_added_by_ai", 0
                ),
                "entities_modified_by_ai": document.metadata.get(
                    "entities_modified_by_ai", 0
                ),
                "parsing_confidence": 0.0,
                "model_versions": document.metadata.get("model_versions", {}),
                "resume_id": getattr(document, "resume_id", None),
                "job_id": getattr(document, "job_id", None),
            },
        }
        document.final_json = validate_and_score(raw_dict)
        document.validation_results = True

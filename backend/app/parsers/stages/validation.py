from datetime import datetime
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import ResumeDocument, PipelineContext
from app.parsers.resume_validator import validate_and_score

class ValidationStage(BaseParserStage):
    def run(self, document: ResumeDocument, context: PipelineContext) -> None:
        extracted = document.normalized_entities
        
        raw_dict = {
            "personal_info": extracted.get("personal_info", {}),
            "summary": extracted.get("summary"),
            "skills": extracted.get("skills", []),
            "education": extracted.get("education", []),
            "experience": extracted.get("experience", []),
            "projects": extracted.get("projects", []),
            "certifications": extracted.get("certifications", []),
            "achievements": extracted.get("achievements", []),
            "languages": extracted.get("languages", []),
            "raw_data": {
                "sections": document.sections
            },
            "metadata": {
                "parser_version": "1.3.0",
                "schema_version": "1.0.0",
                "parsed_at": datetime.utcnow().isoformat() + "Z",
                "processing_time_ms": 0,
                "page_count": document.metadata.get("page_count", 0),
                "word_count": document.metadata.get("word_count", 0),
                "sections_detected": list(document.sections.keys()),
                "entities_detected": 0,
                "parsing_confidence": 0.0,
                "resume_id": document.resume_id,
                "job_id": document.job_id
            }
        }
        
        document.final_json = validate_and_score(raw_dict)
        document.validation_results = True

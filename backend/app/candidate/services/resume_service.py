import os
import uuid
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.candidate.repositories.candidate import resume_repo, candidate_repo
from app.candidate.models.candidate import CandidateResume
from app.candidate.services.timeline_service import timeline_service

# For processing
from app.parsers.core.document import ResumeDocument
from app.parsers.pipeline import ParserPipeline
from app.parsers.stages.extraction import PDFExtractionStage
from app.parsers.stages.cleaning import TextCleaningStage
from app.parsers.stages.section_detection import SectionDetectionStage
from app.parsers.stages.entity_extraction import EntityExtractionStage
from app.parsers.stages.spacy_ner import SpacyNERStage
from app.parsers.stages.hf_ner import HuggingFaceNERStage
from app.parsers.stages.entity_fusion import EntityFusionStage
from app.parsers.stages.normalization import NormalizationStage
from app.parsers.stages.validation import ValidationStage

logger = logging.getLogger(__name__)

def get_default_pipeline() -> ParserPipeline:
    return ParserPipeline([
        PDFExtractionStage(),
        TextCleaningStage(),
        SectionDetectionStage(),
        EntityExtractionStage(),
        SpacyNERStage(),
        HuggingFaceNERStage(),
        EntityFusionStage(),
        NormalizationStage(),
        ValidationStage()
    ])

class ResumeService:
    def upload_resume(self, db: Session, candidate_id: str, file_bytes: bytes, filename: str, content_type: str, user_id: Optional[str] = None) -> CandidateResume:
        candidate = candidate_repo.get(db, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found.")

        # Save file to disk
        unique_filename = f"{uuid.uuid4().hex}.pdf"
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)
            
        initial_metadata = {
            "original_filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_bytes)
        }
        
        # Deactivate older resumes
        resume_repo.deactivate_all_for_candidate(db, candidate_id)
        
        # Create new resume record
        resume = resume_repo.create(db, {
            "candidate_id": candidate_id,
            "filename": unique_filename,
            "parsed_metadata": initial_metadata,
            "is_active": True
        })
        
        timeline_service.log_event(
            db=db,
            candidate_id=candidate_id,
            event_type="resume_uploaded",
            details={"resume_id": resume.id, "original_filename": filename},
            user_id=user_id
        )
        
        return resume

    def process_resume(self, db: Session, resume_id: str):
        resume = resume_repo.get(db, resume_id)
        if not resume:
            logger.error(f"Resume {resume_id} not found for processing.")
            return

        file_path = os.path.join("uploads", resume.filename)
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} not found for resume {resume_id}.")
            return
            
        document = ResumeDocument(file_path=file_path, resume_id=resume.id)
        pipeline = get_default_pipeline()
        
        try:
            document = pipeline.run(document)
            structured_data = document.final_json
            clean_pdf_text = "\n".join([line["text"] for line in document.cleaned_lines])
            
            import copy
            new_metadata = copy.deepcopy(resume.parsed_metadata) if resume.parsed_metadata else {}
            new_metadata["structured_data"] = structured_data
            new_metadata["raw_text"] = clean_pdf_text
            
            resume = resume_repo.update(db, resume, {
                "parsed_metadata": new_metadata,
                "parser_version": "2.2.5" # Track parser version
            })
            
            timeline_service.log_event(
                db=db,
                candidate_id=resume.candidate_id,
                event_type="resume_parsed",
                details={"resume_id": resume.id, "status": "success"},
                user_id="system"
            )
            
            # Fire sync event for Search & Feature Vectors
            from app.candidate.events.sync import sync_candidate_intelligence
            sync_candidate_intelligence(db, resume.candidate_id)
            
            logger.info(f"Resume {resume_id} processed successfully.")
            
        except Exception as e:
            logger.error(f"Pipeline error for Resume {resume_id}: {e}")
            timeline_service.log_event(
                db=db,
                candidate_id=resume.candidate_id,
                event_type="resume_parsed",
                details={"resume_id": resume.id, "status": "failed", "error": str(e)},
                user_id="system"
            )

resume_service = ResumeService()

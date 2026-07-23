import logging
import os
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.job.models.job import JobDescription
from app.job.repositories.job import job_description_repo, job_repo
from app.job.services.timeline_service import timeline_service
# For processing
from app.parsers.core.document import JobDocument
from app.parsers.pipeline import ParserPipeline
from app.parsers.stages.cleaning import TextCleaningStage
from app.parsers.stages.entity_extraction import EntityExtractionStage
from app.parsers.stages.entity_fusion import EntityFusionStage
from app.parsers.stages.extraction import PDFExtractionStage
from app.parsers.stages.hf_ner import HuggingFaceNERStage
from app.parsers.stages.normalization import NormalizationStage
from app.parsers.stages.section_detection import SectionDetectionStage
from app.parsers.stages.spacy_ner import SpacyNERStage

logger = logging.getLogger(__name__)


def get_job_pipeline() -> ParserPipeline:
    return ParserPipeline(
        [
            PDFExtractionStage(),
            TextCleaningStage(),
            SectionDetectionStage(),
            EntityExtractionStage(),
            SpacyNERStage(),
            HuggingFaceNERStage(),
            EntityFusionStage(),
            NormalizationStage(),
            # Job documents might not use full Candidate Validation stage
        ]
    )


class JobDescriptionService:
    def upload_description(
        self,
        db: Session,
        job_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        user_id: Optional[str] = None,
    ) -> JobDescription:
        job = job_repo.get(db, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found.")

        unique_filename = f"{uuid.uuid4().hex}.pdf"
        os.makedirs("uploads/jobs", exist_ok=True)
        file_path = os.path.join("uploads/jobs", unique_filename)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        initial_metadata = {
            "original_filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_bytes),
        }

        job_description_repo.deactivate_all_for_job(db, job_id)

        jd = job_description_repo.create(
            db,
            {
                "job_id": job_id,
                "filename": unique_filename,
                "parsed_metadata": initial_metadata,
                "is_active": True,
            },
        )

        timeline_service.log_event(
            db=db,
            job_id=job_id,
            event_type="jd_uploaded",
            details={"jd_id": jd.id, "original_filename": filename},
            user_id=user_id,
        )

        return jd

    def process_description(self, db: Session, jd_id: str):
        jd = job_description_repo.get(db, jd_id)
        if not jd:
            logger.error(f"Job Description {jd_id} not found.")
            return

        file_path = os.path.join("uploads/jobs", jd.filename)
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} not found for JD {jd_id}.")
            return

        document = JobDocument(file_path=file_path, job_id=jd.job_id)
        pipeline = get_job_pipeline()

        try:
            document = pipeline.run(document)
            structured_data = document.final_json
            clean_pdf_text = "\n".join(
                [line["text"] for line in document.cleaned_lines]
            )

            import copy

            new_metadata = (
                copy.deepcopy(jd.parsed_metadata) if jd.parsed_metadata else {}
            )
            new_metadata["structured_data"] = structured_data
            new_metadata["raw_text"] = clean_pdf_text

            jd = job_description_repo.update(
                db, jd, {"parsed_metadata": new_metadata, "parser_version": "2.2.5"}
            )

            timeline_service.log_event(
                db=db,
                job_id=jd.job_id,
                event_type="jd_parsed",
                details={"jd_id": jd.id, "status": "success"},
                user_id="system",
            )

            from app.job.events.sync import sync_job_intelligence

            sync_job_intelligence(db, jd.job_id)

            logger.info(f"Job Description {jd_id} processed successfully.")

        except Exception as e:
            logger.error(f"Pipeline error for JD {jd_id}: {e}")
            timeline_service.log_event(
                db=db,
                job_id=jd.job_id,
                event_type="jd_parsed",
                details={"jd_id": jd.id, "status": "failed", "error": str(e)},
                user_id="system",
            )


job_description_service = JobDescriptionService()

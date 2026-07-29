"""Resume service.

Orchestrates the full resume lifecycle:
1. Validate the PDF bytes.
2. Detect duplicates via SHA-256 hash.
3. Persist the file and create a CandidateResume record.
4. Build the parser pipeline (respecting feature flags).
5. Run the pipeline in the background.
6. Compute completeness + health report and persist to resume_analysis.
"""

import copy
import hashlib
import logging
import os
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.candidate.models.candidate import CandidateResume
from app.candidate.repositories.candidate import candidate_repo, resume_repo
from app.candidate.services.timeline_service import timeline_service
from app.intelligence.service import resume_intelligence_service
from app.parsers.completeness import analyze_completeness
from app.parsers.core.config_loader import load_config
from app.parsers.core.document import ResumeDocument
from app.parsers.core.version import PARSER_VERSION
from app.parsers.health_report import generate_health_report
from app.parsers.pdf_validator import PDFValidationError, validate_pdf
from app.parsers.pipeline import ParserPipeline
from app.parsers.stages.cleaning import TextCleaningStage
from app.parsers.stages.entity_extraction import EntityExtractionStage
from app.parsers.stages.entity_fusion import EntityFusionStage
from app.parsers.stages.extraction import PDFExtractionStage
from app.parsers.stages.hf_ner import HuggingFaceNERStage
from app.parsers.stages.normalization import NormalizationStage
from app.parsers.stages.section_detection import SectionDetectionStage
from app.parsers.stages.spacy_ner import SpacyNERStage
from app.parsers.stages.validation import ValidationStage

logger = logging.getLogger(__name__)


def get_default_pipeline() -> ParserPipeline:
    """Build the parser pipeline respecting feature flags from YAML config.

    Stages are conditionally included based on ``parser_feature_flags.yaml``.
    This allows lightweight environments (CI, low-memory deployments) to
    disable GPU-heavy NER stages without touching Python code.

    The list of active flag names is stored so it can be recorded in the
    final parsed output for traceability.
    """
    flags = (
        load_config("parser_feature_flags.yaml")
        .get("parser", {})
        .get("feature_flags", {})
    )

    active_flags: list[str] = []
    stages = [
        PDFExtractionStage(),
        TextCleaningStage(),
        SectionDetectionStage(),
        EntityExtractionStage(),
    ]

    if flags.get("spacy_ner", True):
        stages.append(SpacyNERStage())
        active_flags.append("spacy_ner")

    if flags.get("hf_ner", True):
        stages.append(HuggingFaceNERStage())
        active_flags.append("hf_ner")

    if flags.get("entity_fusion", True):
        stages.append(EntityFusionStage())
        active_flags.append("entity_fusion")

    stages += [NormalizationStage(), ValidationStage()]

    # Record active flags so they flow into document.metadata → final_json.metadata
    pipeline = ParserPipeline(stages)
    pipeline.active_flags = active_flags  # type: ignore[attr-defined]
    return pipeline


class ResumeService:
    """Service layer for resume upload and processing.

    Enforces DDD boundaries:
    - No business logic in the API layer.
    - No direct DB access from the parser pipeline.
    - Completeness and health analysis live outside the pipeline.
    """

    def upload_resume(
        self,
        db: Session,
        candidate_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        user_id: Optional[str] = None,
    ) -> CandidateResume:
        """Validate, deduplicate, persist, and enqueue a resume for processing.

        Steps:
        1. Validate PDF bytes (magic bytes, size, page count, encryption).
        2. Compute SHA-256 hash for global deduplication.
        3. If hash matches an existing parsed resume, create a new record
           for this candidate and copy the parsed data — skip re-parsing.
        4. Otherwise, save the file and create a new record for background processing.

        Args:
            db:           Database session.
            candidate_id: ID of the candidate uploading the resume.
            file_bytes:   Raw bytes of the uploaded file.
            filename:     Original filename from the upload request.
            content_type: MIME type from the upload request.
            user_id:      Optional identity of the uploading user (for audit).

        Returns:
            The newly created ``CandidateResume`` ORM record.

        Raises:
            ValueError:        If the candidate does not exist.
            PDFValidationError: If the PDF fails any validation check.
        """
        candidate = candidate_repo.get(db, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found.")

        # Step 1: Validate PDF before touching the filesystem.
        upload_cfg = load_config("upload_config.yaml")
        validate_pdf(file_bytes, upload_cfg)

        # Step 2: Compute hash for global deduplication.
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # Step 3: Check for globally duplicate file.
        existing = resume_repo.get_by_hash(db, file_hash)
        if existing and existing.parsed_metadata:
            return self._create_duplicate_record(
                db=db,
                candidate_id=candidate_id,
                filename=filename,
                content_type=content_type,
                file_hash=file_hash,
                source_resume=existing,
                user_id=user_id,
            )

        # Step 4: New file — persist to disk and create record.
        return self._create_new_record(
            db=db,
            candidate_id=candidate_id,
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type,
            file_hash=file_hash,
            user_id=user_id,
        )

    def _create_duplicate_record(
        self,
        db: Session,
        candidate_id: str,
        filename: str,
        content_type: str,
        file_hash: str,
        source_resume: CandidateResume,
        user_id: Optional[str],
    ) -> CandidateResume:
        """Create a new resume record by copying parsed data from a duplicate.

        The candidate identity is always preserved — we create a new record
        for this candidate and copy the expensive parsing output. The source
        resume record is never modified or shared.
        """
        logger.info(
            "Duplicate PDF detected (hash=%s). Copying parsed data from resume %s.",
            file_hash,
            source_resume.id,
        )

        resume_repo.deactivate_all_for_candidate(db, candidate_id)

        # Copy parsed data from the matched resume
        copied_metadata = copy.deepcopy(source_resume.parsed_metadata or {})
        copied_metadata["original_filename"] = filename
        copied_metadata["content_type"] = content_type
        copied_metadata["duplicate_of"] = source_resume.id

        resume = resume_repo.create(
            db,
            {
                "candidate_id": candidate_id,
                "filename": source_resume.filename,  # Reuse the same stored file
                "parsed_metadata": copied_metadata,
                "resume_analysis": copy.deepcopy(source_resume.resume_analysis),
                "candidate_profile": copy.deepcopy(source_resume.candidate_profile),
                "parser_version": PARSER_VERSION,
                "file_hash": file_hash,
                "is_active": True,
            },
        )

        timeline_service.log_event(
            db=db,
            candidate_id=candidate_id,
            event_type="resume_duplicate_detected",
            details={
                "resume_id": resume.id,
                "source_resume_id": source_resume.id,
                "original_filename": filename,
            },
            user_id=user_id or "system",
        )

        return resume

    def _create_new_record(
        self,
        db: Session,
        candidate_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        file_hash: str,
        user_id: Optional[str],
    ) -> CandidateResume:
        """Save the file to disk and create a new resume record."""
        unique_filename = f"{uuid.uuid4().hex}.pdf"
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", unique_filename)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        initial_metadata = {
            "original_filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_bytes),
        }

        resume_repo.deactivate_all_for_candidate(db, candidate_id)

        resume = resume_repo.create(
            db,
            {
                "candidate_id": candidate_id,
                "filename": unique_filename,
                "parsed_metadata": initial_metadata,
                "file_hash": file_hash,
                "is_active": True,
            },
        )

        timeline_service.log_event(
            db=db,
            candidate_id=candidate_id,
            event_type="resume_uploaded",
            details={"resume_id": resume.id, "original_filename": filename},
            user_id=user_id,
        )

        return resume

    def process_resume(self, db: Session, resume_id: str) -> None:
        """Run the full parser pipeline and post-parse analysis for a resume.

        This method is intended to run as a background task after upload.

        Steps:
        1. Fetch the resume record and verify the file exists.
        2. Run the ParserPipeline (stages controlled by feature flags).
        3. Compute completeness score + health report.
        4. Persist all results to the resume record.
        5. Trigger the candidate intelligence sync.
        """
        resume = resume_repo.get(db, resume_id)
        if not resume:
            logger.error("Resume %s not found for processing.", resume_id)
            return

        file_path = os.path.join("uploads", resume.filename)
        if not os.path.exists(file_path):
            logger.error("File %s not found for resume %s.", file_path, resume_id)
            return

        document = ResumeDocument(file_path=file_path, resume_id=resume.id)
        pipeline = get_default_pipeline()

        # Propagate active feature flags into the document so they appear in final_json.
        active_flags = getattr(pipeline, "active_flags", [])
        document.metadata["feature_flags_active"] = active_flags

        try:
            document = pipeline.run(document)
            structured_data: dict = document.final_json
            clean_pdf_text = "\n".join(
                line["text"] for line in document.cleaned_lines
            )

            new_metadata = copy.deepcopy(resume.parsed_metadata or {})
            new_metadata["structured_data"] = structured_data
            new_metadata["raw_text"] = clean_pdf_text

            # --- Post-parse analysis (feature-flag guarded) ---
            flags = (
                load_config("parser_feature_flags.yaml")
                .get("parser", {})
                .get("feature_flags", {})
            )

            resume_analysis: dict = {}

            if flags.get("completeness", True):
                resume_analysis["completeness"] = analyze_completeness(structured_data)

            if flags.get("health_report", True):
                resume_analysis["health_report"] = generate_health_report(
                    structured_data
                )

            # --- Phase 2 Resume Intelligence Engine ---
            profile = resume_intelligence_service.generate_profile(
                candidate_id=resume.candidate_id,
                resume_id=resume.id,
                parsed_metadata=structured_data,
                resume_analysis=resume_analysis,
            )
            candidate_profile_json = profile.model_dump(mode="json")

            resume = resume_repo.update(
                db,
                resume,
                {
                    "parsed_metadata": new_metadata,
                    "resume_analysis": resume_analysis or None,
                    "candidate_profile": candidate_profile_json,
                    "parser_version": PARSER_VERSION,
                },
            )

            timeline_service.log_event(
                db=db,
                candidate_id=resume.candidate_id,
                event_type="resume_parsed",
                details={"resume_id": resume.id, "status": "success"},
                user_id="system",
            )

            # Trigger downstream intelligence sync
            from app.candidate.events.sync import sync_candidate_intelligence

            sync_candidate_intelligence(db, resume.candidate_id)

            logger.info("Resume %s processed successfully.", resume_id)

        except Exception as exc:
            logger.error("Pipeline error for Resume %s: %s", resume_id, exc)
            timeline_service.log_event(
                db=db,
                candidate_id=resume.candidate_id,
                event_type="resume_parsed",
                details={
                    "resume_id": resume.id,
                    "status": "failed",
                    "error": str(exc),
                },
                user_id="system",
            )


resume_service = ResumeService()

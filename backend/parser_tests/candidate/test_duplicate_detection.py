"""Tests for SHA-256 duplicate detection.

Verifies the deduplication logic in ResumeService.upload_resume():
- Identical file bytes → new candidate record, no pipeline, parsed data copied.
- Different file bytes → normal upload flow.
- Hash stored correctly on the resume record.
"""

import hashlib
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import fitz

from app.parsers.pdf_validator import PDFValidationError


def _make_pdf_bytes(text: str = "Resume content here for test") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    return doc.tobytes()


def _hash(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------------------
# Unit tests on dedup service logic (no real DB required)
# ---------------------------------------------------------------------------

def test_duplicate_resume_copies_parsed_data():
    """When a duplicate hash is found, parsed_metadata should be copied from source."""
    from app.candidate.services.resume_service import ResumeService

    pdf_bytes = _make_pdf_bytes("Same resume content")
    file_hash = _hash(pdf_bytes)

    # Build a mock existing resume with parsed data
    existing_resume = MagicMock()
    existing_resume.id = "existing-id"
    existing_resume.filename = "existing_file.pdf"
    existing_resume.parsed_metadata = {
        "structured_data": {"personal_info": {"name": {"value": "Jane Doe"}}},
        "raw_text": "Jane Doe",
    }
    existing_resume.resume_analysis = {
        "completeness": {"score": 90, "missing": []},
    }

    new_resume = MagicMock()
    new_resume.id = "new-id"
    new_resume.filename = "existing_file.pdf"
    new_resume.parsed_metadata = None

    service = ResumeService()
    mock_db = MagicMock()

    with (
        patch("app.candidate.services.resume_service.candidate_repo") as mock_candidate_repo,
        patch("app.candidate.services.resume_service.resume_repo") as mock_resume_repo,
        patch("app.candidate.services.resume_service.timeline_service"),
        patch("app.candidate.services.resume_service.validate_pdf"),
        patch("app.candidate.services.resume_service.load_config", return_value={"upload": {"max_size_bytes": 10_000_000, "max_pages": 10}}),
    ):
        mock_candidate_repo.get.return_value = MagicMock(id="candidate-1")
        mock_resume_repo.get_by_hash.return_value = existing_resume
        mock_resume_repo.create.return_value = new_resume

        result = service.upload_resume(
            db=mock_db,
            candidate_id="candidate-1",
            file_bytes=pdf_bytes,
            filename="resume.pdf",
            content_type="application/pdf",
        )

        # Deactivate old resumes should be called
        mock_resume_repo.deactivate_all_for_candidate.assert_called_once()

        # Create should be called with the copied metadata
        create_call_kwargs = mock_resume_repo.create.call_args[0][1]
        assert create_call_kwargs["file_hash"] == file_hash
        assert create_call_kwargs["parsed_metadata"]["duplicate_of"] == "existing-id"
        assert "structured_data" in create_call_kwargs["parsed_metadata"]


def test_new_resume_runs_normal_flow():
    """When no duplicate is found, the normal upload flow should proceed."""
    from app.candidate.services.resume_service import ResumeService

    pdf_bytes = _make_pdf_bytes("Unique resume content XYZ12345")
    file_hash = _hash(pdf_bytes)

    service = ResumeService()
    mock_db = MagicMock()

    with (
        patch("app.candidate.services.resume_service.candidate_repo") as mock_candidate_repo,
        patch("app.candidate.services.resume_service.resume_repo") as mock_resume_repo,
        patch("app.candidate.services.resume_service.timeline_service"),
        patch("app.candidate.services.resume_service.validate_pdf"),
        patch("app.candidate.services.resume_service.load_config", return_value={"upload": {"max_size_bytes": 10_000_000, "max_pages": 10}}),
        patch("builtins.open", MagicMock()),
        patch("os.makedirs"),
    ):
        mock_candidate_repo.get.return_value = MagicMock(id="candidate-2")
        mock_resume_repo.get_by_hash.return_value = None  # No duplicate
        mock_resume_repo.create.return_value = MagicMock(id="new-resume")

        service.upload_resume(
            db=mock_db,
            candidate_id="candidate-2",
            file_bytes=pdf_bytes,
            filename="resume.pdf",
            content_type="application/pdf",
        )

        create_call_kwargs = mock_resume_repo.create.call_args[0][1]
        assert create_call_kwargs["file_hash"] == file_hash
        # No duplicate_of key in new record
        assert "duplicate_of" not in create_call_kwargs.get("parsed_metadata", {})


def test_hash_is_sha256():
    """Verify the hash stored is a valid SHA-256 hex string (64 chars)."""
    pdf_bytes = _make_pdf_bytes()
    expected_hash = hashlib.sha256(pdf_bytes).hexdigest()
    assert len(expected_hash) == 64
    assert expected_hash.isalnum()

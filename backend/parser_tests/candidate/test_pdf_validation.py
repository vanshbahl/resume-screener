"""Tests for secure PDF validation.

Tests the ``validate_pdf`` function against each failure mode.
No database, no pipeline, no file system writes.
"""

import fitz
import pytest

from app.parsers.pdf_validator import PDFValidationError, validate_pdf

_DEFAULT_CFG = {"upload": {"max_size_bytes": 1_048_576, "max_pages": 5}}


def _make_valid_pdf(page_count: int = 1, text: str = "Hello World") -> bytes:
    """Generate a minimal valid PDF in memory."""
    doc = fitz.open()
    for _ in range(page_count):
        page = doc.new_page()
        page.insert_text((72, 72), text)
    return doc.tobytes()


def _make_encrypted_pdf() -> bytes:
    """Generate a password-protected PDF using PyMuPDF save encryption."""
    import tempfile, os
    doc = fitz.open()
    doc.new_page()
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc.save(
        tmp.name,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw="owner",
        user_pw="user",
    )
    doc.close()
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.remove(tmp.name)
    return data


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_pdf_passes():
    """A well-formed, non-encrypted, single-page PDF should pass all checks."""
    pdf_bytes = _make_valid_pdf()
    validate_pdf(pdf_bytes, _DEFAULT_CFG)  # No exception


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

def test_invalid_magic_bytes():
    """File not starting with %PDF should raise INVALID_FORMAT."""
    bad_bytes = b"PK\x03\x04" + b"\x00" * 100  # ZIP header
    with pytest.raises(PDFValidationError) as exc_info:
        validate_pdf(bad_bytes, _DEFAULT_CFG)
    assert exc_info.value.code == "INVALID_FORMAT"


def test_file_too_large():
    """File exceeding max_size_bytes should raise FILE_TOO_LARGE."""
    pdf_bytes = _make_valid_pdf()
    tiny_cfg = {"upload": {"max_size_bytes": 10, "max_pages": 5}}
    with pytest.raises(PDFValidationError) as exc_info:
        validate_pdf(pdf_bytes, tiny_cfg)
    assert exc_info.value.code == "FILE_TOO_LARGE"


def test_too_many_pages():
    """PDF with more pages than max_pages should raise TOO_MANY_PAGES."""
    pdf_bytes = _make_valid_pdf(page_count=3)
    strict_cfg = {"upload": {"max_size_bytes": 10_000_000, "max_pages": 2}}
    with pytest.raises(PDFValidationError) as exc_info:
        validate_pdf(pdf_bytes, strict_cfg)
    assert exc_info.value.code == "TOO_MANY_PAGES"


def test_password_protected_pdf():
    """An encrypted PDF should raise PASSWORD_PROTECTED."""
    pdf_bytes = _make_encrypted_pdf()
    with pytest.raises(PDFValidationError) as exc_info:
        validate_pdf(pdf_bytes, _DEFAULT_CFG)
    assert exc_info.value.code == "PASSWORD_PROTECTED"


def test_corrupted_pdf():
    """Truncated or malformed PDF bytes should raise CORRUPTED_PDF."""
    corrupted = b"%PDF-1.4 \x00\xff\xff\xff truncated"
    with pytest.raises(PDFValidationError) as exc_info:
        validate_pdf(corrupted, _DEFAULT_CFG)
    assert exc_info.value.code == "CORRUPTED_PDF"


# ---------------------------------------------------------------------------
# Error detail content
# ---------------------------------------------------------------------------

def test_error_detail_is_human_readable():
    """Validation errors should contain human-friendly messages."""
    bad_bytes = b"not a pdf at all"
    with pytest.raises(PDFValidationError) as exc_info:
        validate_pdf(bad_bytes, _DEFAULT_CFG)
    assert len(exc_info.value.detail) > 20  # Not an empty or cryptic message

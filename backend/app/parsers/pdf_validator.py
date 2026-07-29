"""Secure PDF validation module.

This module performs all pre-persistence checks on uploaded PDF bytes.
It is a standalone collection of pure functions — not a pipeline stage —
because validation must occur *before* the file is written to disk and
*before* the ParserPipeline is instantiated.

Usage::

    from app.parsers.pdf_validator import validate_pdf, PDFValidationError

    try:
        validate_pdf(file_bytes, config)
    except PDFValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
"""

import fitz  # PyMuPDF — already a project dependency

# PDF magic bytes — all valid PDF files start with this 4-byte sequence.
_PDF_MAGIC: bytes = b"%PDF"


class PDFValidationError(ValueError):
    """Raised when an uploaded file fails any PDF validation check.

    Attributes:
        code:   Machine-readable error code (e.g. ``INVALID_FORMAT``).
        detail: Human-readable description suitable for API error responses.
    """

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def validate_pdf(file_bytes: bytes, config: dict) -> None:
    """Validate PDF bytes against all security and format constraints.

    Checks are performed in order of cost — cheap checks first so that
    expensive I/O is only reached if the cheap checks pass.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        config:     ``upload`` section of ``upload_config.yaml``
                    (keys: ``max_size_bytes``, ``max_pages``).

    Raises:
        PDFValidationError: On any validation failure with a specific ``code``.
    """
    upload_cfg = config.get("upload", config)  # accept both full config and subsection

    _check_magic_bytes(file_bytes)
    _check_file_size(file_bytes, upload_cfg.get("max_size_bytes", 10_485_760))
    _check_pdf_integrity(file_bytes, upload_cfg.get("max_pages", 10))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _check_magic_bytes(file_bytes: bytes) -> None:
    """Verify the file starts with the PDF magic byte sequence."""
    if len(file_bytes) < 4 or file_bytes[:4] != _PDF_MAGIC:
        raise PDFValidationError(
            code="INVALID_FORMAT",
            detail=(
                "The uploaded file is not a valid PDF. "
                "Only PDF documents are accepted."
            ),
        )


def _check_file_size(file_bytes: bytes, max_size_bytes: int) -> None:
    """Verify the file does not exceed the configured maximum size."""
    if len(file_bytes) > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise PDFValidationError(
            code="FILE_TOO_LARGE",
            detail=(
                f"The uploaded file exceeds the maximum allowed size of "
                f"{max_mb:.0f} MB. Please reduce the file size and try again."
            ),
        )


def _check_pdf_integrity(file_bytes: bytes, max_pages: int) -> None:
    """Open the PDF with PyMuPDF to detect corruption, encryption, and page limits.

    Using PyMuPDF (already a project dependency) avoids introducing any new
    library. A single ``fitz.open()`` call surfaces all three issues.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception:
        raise PDFValidationError(
            code="CORRUPTED_PDF",
            detail=(
                "The uploaded PDF appears to be corrupted or malformed and "
                "cannot be processed. Please re-export the file and try again."
            ),
        )

    if doc.is_encrypted:
        doc.close()
        raise PDFValidationError(
            code="PASSWORD_PROTECTED",
            detail=(
                "The uploaded PDF is password-protected. "
                "Please remove the password and try again."
            ),
        )

    page_count = len(doc)
    doc.close()

    if page_count > max_pages:
        raise PDFValidationError(
            code="TOO_MANY_PAGES",
            detail=(
                f"The uploaded PDF has {page_count} pages, which exceeds the "
                f"maximum of {max_pages} pages. Please upload a shorter resume."
            ),
        )

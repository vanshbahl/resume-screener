"""Tests for OCR fallback integration.

Uses a MockOCRProvider so no PaddleOCR model weights are needed.
Tests verify:
- OCR is triggered when native text is below the threshold.
- OCR is skipped when text is sufficient.
- OCR provider unavailability degrades gracefully (no crash).
"""

import os
import tempfile

import pytest

from app.parsers.core.document import PipelineContext, ResumeDocument
from app.parsers.stages.extraction import PDFExtractionStage


class MockOCRProvider:
    """Minimal mock that satisfies the OCRProvider protocol."""

    def __init__(self, available: bool = True, text: str = "OCR extracted text line one\nOCR extracted text line two"):
        self._available = available
        self._text = text
        self.called = False

    def is_available(self) -> bool:
        return self._available

    def extract_text(self, file_path: str) -> str:
        self.called = True
        return self._text


@pytest.fixture
def sparse_pdf_path():
    """Create a real but nearly empty PDF (very sparse text)."""
    import fitz

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc = fitz.open()
    doc.new_page()  # blank page — no text
    doc.save(tmp.name)
    doc.close()
    yield tmp.name
    os.remove(tmp.name)


@pytest.fixture
def normal_pdf_path():
    """Create a PDF with sufficient text to avoid OCR fallback."""
    import fitz

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "John Doe\nSoftware Engineer\nExperience: 5 years at Acme Corp")
    doc.save(tmp.name)
    doc.close()
    yield tmp.name
    os.remove(tmp.name)


def _make_stage(provider, min_chars=100):
    """Build a PDFExtractionStage with injected provider and config override."""
    stage = PDFExtractionStage(ocr_provider=provider)
    # Override config so threshold is predictable in tests
    stage._ocr_config = {"enabled": True, "min_text_chars": min_chars, "render_scale": 1.0}
    return stage


def test_ocr_triggered_on_sparse_pdf(sparse_pdf_path):
    """OCR should run when native extraction yields fewer chars than the threshold."""
    mock = MockOCRProvider()
    stage = _make_stage(mock, min_chars=50)

    document = ResumeDocument(file_path=sparse_pdf_path)
    context = PipelineContext()
    stage.run(document, context)

    assert mock.called, "OCR provider should have been called for a sparse PDF."
    assert document.metadata.get("ocr_triggered") is True
    # Lines should be populated from OCR output
    assert any("OCR extracted" in line["text"] for line in document.raw_lines)


def test_ocr_skipped_on_normal_pdf(normal_pdf_path):
    """OCR should NOT run when native extraction produces sufficient text."""
    mock = MockOCRProvider()
    stage = _make_stage(mock, min_chars=10)  # text will exceed 10 chars

    document = ResumeDocument(file_path=normal_pdf_path)
    context = PipelineContext()
    stage.run(document, context)

    assert not mock.called, "OCR provider should NOT be called when text is sufficient."
    assert document.metadata.get("ocr_triggered") is False


def test_ocr_unavailable_degrades_gracefully(sparse_pdf_path):
    """When OCR provider is unavailable, the stage should not crash."""
    mock = MockOCRProvider(available=False)
    stage = _make_stage(mock, min_chars=50)

    document = ResumeDocument(file_path=sparse_pdf_path)
    context = PipelineContext()

    # Should not raise
    stage.run(document, context)

    assert not mock.called
    # A warning should be logged
    warning_codes = [w.type for w in context.warnings]
    assert "OCRProviderUnavailable" in warning_codes


def test_ocr_disabled_via_config(sparse_pdf_path):
    """When ocr.enabled is False in config, OCR never runs."""
    mock = MockOCRProvider()
    stage = PDFExtractionStage(ocr_provider=mock)
    stage._ocr_config = {"enabled": False, "min_text_chars": 50}

    document = ResumeDocument(file_path=sparse_pdf_path)
    context = PipelineContext()
    stage.run(document, context)

    assert not mock.called, "OCR should be skipped when disabled in config."

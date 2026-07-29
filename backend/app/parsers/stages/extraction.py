"""PDF text extraction stage with OCR fallback.

Normal path: PyMuPDF (fitz) native text extraction — fast, no model weights.
Fallback path: OCR provider (PaddleOCR by default) triggered when native
extraction yields fewer characters than the configured threshold.

The OCR provider is injected via the constructor so tests can pass a
lightweight MockOCRProvider without loading real model weights.
"""

import logging
from typing import Optional

import fitz

from app.parsers.core.base import BaseParserStage
from app.parsers.core.config_loader import load_config
from app.parsers.core.document import BaseDocument, PipelineContext
from app.parsers.core.exceptions import ParserFatalError
from app.parsers.ocr.base import OCRProvider

logger = logging.getLogger(__name__)


class PDFExtractionStage(BaseParserStage):
    """Extracts raw text from PDF files with an optional OCR fallback.

    Args:
        ocr_provider: An optional :class:`OCRProvider` instance.
            If ``None``, defaults to :class:`PaddleOCRProvider` on first use.
            Pass a mock implementation in tests to avoid loading real models.
    """

    def __init__(self, ocr_provider: Optional[OCRProvider] = None) -> None:
        self._ocr_provider = ocr_provider
        self._ocr_config: dict = load_config("ocr_config.yaml").get("ocr", {})

    def _get_ocr_provider(self) -> OCRProvider:
        """Return the OCR provider, defaulting to PaddleOCRProvider."""
        if self._ocr_provider is None:
            from app.parsers.ocr.paddle_provider import PaddleOCRProvider

            self._ocr_provider = PaddleOCRProvider()
        return self._ocr_provider

    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        if document.raw_lines:
            return  # Skip if pre-populated (e.g., by unit tests)

        lines: list[dict] = []
        word_count = 0
        line_index = 0
        page_count = 0
        total_chars = 0

        try:
            if document.file_path.endswith(".txt"):
                # Plain-text fallback for test fixtures
                with open(document.file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                page_count = 1
                for line in text.split("\n"):
                    cleaned_line = line.strip()
                    if cleaned_line:
                        lines.append(
                            {"text": cleaned_line, "page": 1, "line_no": line_index}
                        )
                        word_count += len(cleaned_line.split())
                        total_chars += len(cleaned_line)
                    line_index += 1
            else:
                doc = fitz.open(document.file_path)
                page_count = len(doc)

                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text()
                    page_lines = text.split("\n")

                    for line in page_lines:
                        cleaned_line = line.strip()
                        if cleaned_line:
                            lines.append(
                                {
                                    "text": cleaned_line,
                                    "page": page_num,
                                    "line_no": line_index,
                                }
                            )
                            word_count += len(cleaned_line.split())
                            total_chars += len(cleaned_line)
                        # Always increment — blank lines create gaps for block-splitting
                        line_index += 1

                doc.close()

                # -------------------------------------------------------
                # OCR Fallback
                # Trigger when native extraction is too sparse to be useful.
                # -------------------------------------------------------
                ocr_enabled = self._ocr_config.get("enabled", True)
                min_chars = self._ocr_config.get("min_text_chars", 100)

                if ocr_enabled and total_chars < min_chars:
                    provider = self._get_ocr_provider()

                    if provider.is_available():
                        context.log_warning(
                            "OCRFallbackTriggered",
                            f"Native extraction yielded only {total_chars} chars "
                            f"(threshold: {min_chars}). Running OCR fallback.",
                        )
                        logger.info(
                            "OCR fallback triggered for %s (chars=%d).",
                            document.file_path,
                            total_chars,
                        )

                        ocr_text = provider.extract_text(document.file_path)
                        document.metadata["ocr_triggered"] = True

                        # Rebuild lines from OCR output
                        lines = []
                        word_count = 0
                        line_index = 0
                        for line in ocr_text.split("\n"):
                            cleaned = line.strip()
                            if cleaned:
                                lines.append(
                                    {"text": cleaned, "page": 1, "line_no": line_index}
                                )
                                word_count += len(cleaned.split())
                            line_index += 1
                    else:
                        logger.warning(
                            "OCR fallback not available for sparse PDF %s.",
                            document.file_path,
                        )
                        context.log_warning(
                            "OCRProviderUnavailable",
                            "Text is sparse but OCR provider is not available.",
                        )

            if page_count == 0 or len(lines) == 0:
                context.log_warning(
                    "EmptyResume", "No text could be extracted from the document."
                )

            document.raw_lines = lines
            document.metadata["page_count"] = page_count
            document.metadata["word_count"] = word_count
            document.metadata.setdefault("ocr_triggered", False)

        except ParserFatalError:
            raise
        except Exception as exc:
            raise ParserFatalError(f"PDF Extraction failed: {exc}") from exc

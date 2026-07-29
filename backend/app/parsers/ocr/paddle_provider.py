"""PaddleOCR implementation of the OCRProvider protocol.

Wraps the existing logic from app/services/extraction.py into the new
provider abstraction. The legacy file is preserved \u2014 this class does not
delete it; it supersedes it within the ParserPipeline.

Design decisions:
- PaddleOCR is lazy-initialized on the first call to ``extract_text()``.
  This avoids loading ~2 GB of model weights on every application start
  for deployments where OCR is rarely or never needed.
- Initialization failure is handled gracefully: ``is_available()`` returns
  False and ``extract_text()`` returns ``""`` so the pipeline degrades
  without crashing.
- All configuration (language, scale, angle classification) is read from
  ``config/ocr_config.yaml`` rather than hardcoded.
"""

import logging
from typing import Optional

import fitz  # PyMuPDF \u2014 already a project dependency
import numpy as np

from app.parsers.core.config_loader import load_config

logger = logging.getLogger(__name__)


class PaddleOCRProvider:
    """PaddleOCR-backed text extraction for scanned PDF documents.

    Satisfies the ``OCRProvider`` protocol via structural subtyping \u2014
    no explicit inheritance from ``OCRProvider`` is required.
    """

    def __init__(self) -> None:
        self._ocr: Optional[object] = None
        self._initialized: bool = False
        self._available: bool = False
        self._config: dict = load_config("ocr_config.yaml").get("ocr", {})

    def _initialize(self) -> None:
        """Lazy-initialize PaddleOCR on first use."""
        if self._initialized:
            return

        self._initialized = True
        try:
            from paddleocr import PaddleOCR  # type: ignore[import]

            self._ocr = PaddleOCR(
                use_angle_cls=self._config.get("use_angle_cls", True),
                lang=self._config.get("language", "en"),
                show_log=False,
            )
            self._available = True
            logger.info("PaddleOCRProvider initialized successfully.")
        except Exception as exc:
            logger.warning(
                "PaddleOCRProvider failed to initialize \u2014 OCR fallback will be "
                "skipped. Install paddleocr to enable this feature. "
                "Error: %s",
                exc,
            )
            self._available = False

    def is_available(self) -> bool:
        """Return True if PaddleOCR loaded successfully."""
        if not self._initialized:
            self._initialize()
        return self._available

    def extract_text(self, file_path: str) -> str:
        """Render each PDF page as an image and run PaddleOCR on it.

        Args:
            file_path: Absolute path to the PDF file.

        Returns:
            Concatenated OCR text from all pages, or ``""`` on any failure.
        """
        if not self.is_available():
            return ""

        scale = self._config.get("render_scale", 2.0)
        extracted_lines: list[str] = []

        try:
            doc = fitz.open(file_path)
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                    pix.h, pix.w, pix.n
                )

                # PaddleOCR expects BGR/RGB \u2014 convert if the image has an alpha channel.
                if pix.n == 4:
                    import cv2  # type: ignore[import]

                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                result = self._ocr.ocr(img, cls=True)  # type: ignore[union-attr]
                if result and result[0]:
                    for line in result[0]:
                        text = line[1][0]
                        if text.strip():
                            extracted_lines.append(text.strip())
            doc.close()
        except Exception as exc:
            logger.warning("PaddleOCRProvider extraction failed: %s", exc)
            return ""

        return "\n".join(extracted_lines)

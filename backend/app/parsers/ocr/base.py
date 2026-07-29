"""OCR provider protocol definition.

Defines the structural interface that all OCR provider implementations must satisfy.
Using ``typing.Protocol`` (structural subtyping) means providers do NOT need to
inherit from this class — they only need to implement the matching methods.

This keeps providers lightweight and avoids forcing PaddleOCR-specific
base classes onto alternative implementations (e.g., Tesseract).
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class OCRProvider(Protocol):
    """Structural interface for OCR text extraction providers.

    Any class that implements ``is_available()`` and ``extract_text()``
    with the correct signatures satisfies this protocol \u2014 no inheritance needed.
    """

    def is_available(self) -> bool:
        """Return True if the provider is ready to process documents.

        A provider may be unavailable if its underlying model failed to load
        (e.g., PaddleOCR weights not downloaded, GPU not available).
        The extraction stage will skip OCR gracefully when this returns False.
        """
        ...

    def extract_text(self, file_path: str) -> str:
        """Extract plain text from a PDF file using OCR.

        Args:
            file_path: Absolute path to the PDF file on disk.

        Returns:
            Extracted text as a single string, or an empty string if extraction
            fails. Implementations must never raise; they must return ``""``
            on any internal failure so the pipeline can continue without OCR.
        """
        ...

"""Publication extractor for academic and professional publications.

Publication formats on resumes are highly inconsistent (APA, MLA, IEEE,
informal one-liners). This extractor uses heuristics to capture whatever
can be deterministically inferred; the ``PublicationEntry`` schema marks
all fields as Optional to reflect this reality.

Detects:
- DOI patterns (``10.NNNN/...``)
- Year (4-digit, 2000+)
- URLs (http/https)
- Author-like comma-separated name lists
- Venue hints (conference / journal keywords)
"""

import re
from typing import Any, Dict, List, Optional


class PublicationExtractor:
    """Deterministic extractor for publication entries."""

    # DOI pattern: starts with ``10.`` followed by registrant code and suffix.
    _DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[^\s,;]+", re.IGNORECASE)

    # HTTP/HTTPS URL pattern.
    _URL_PATTERN = re.compile(
        r"https?://[^\s,;)>\"]+", re.IGNORECASE
    )

    # Year: 2000–2099.
    _YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")

    # Venue keywords that suggest a publication context.
    _VENUE_PATTERN = re.compile(
        r"\b(proceedings|journal|conference|workshop|symposium|"
        r"transactions|letters|arxiv|acm|ieee|springer|elsevier|"
        r"nature|science|plos|frontiers|preprint)\b",
        re.IGNORECASE,
    )

    # Author heuristic: two or more comma-separated tokens that look like names
    # (Capitalized word, optionally followed by initials or another word).
    _AUTHOR_PATTERN = re.compile(
        r"([A-Z][a-z]+(?:\s[A-Z]\.?)?(?:\s[A-Z][a-z]+)?)"
        r"(?:,\s*[A-Z][a-z]+(?:\s[A-Z]\.?)?(?:\s[A-Z][a-z]+)?){1,}",
    )

    _SECTION = "publications"

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def extract(self, lines: List[Dict]) -> List[Dict]:
        """Extract publication entries from section lines.

        Args:
            lines: Cleaned line objects from ``document.sections["publications"]``.

        Returns:
            A list of raw dicts conforming to ``PublicationEntry`` schema.
        """
        if not lines:
            return []

        blocks = self._segment_blocks(lines)
        return [self._parse_block(block) for block in blocks if block]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_field(
        self,
        value: Any,
        confidence: float,
        source_line: Dict,
    ) -> Optional[Dict]:
        if not value:
            return None
        return {
            "value": value,
            "confidence": confidence,
            "source": {
                "page": source_line["page"],
                "section": self._SECTION,
                "line": source_line["line_no"],
            },
            "origin_model": "deterministic",
        }

    def _segment_blocks(self, lines: List[Dict]) -> List[List[Dict]]:
        """Group consecutive lines (no gap > 1) into publication blocks."""
        blocks: List[List[Dict]] = []
        current: List[Dict] = []

        for line_obj in lines:
            if not current:
                current.append(line_obj)
            else:
                if line_obj["line_no"] - current[-1]["line_no"] > 1:
                    blocks.append(current)
                    current = [line_obj]
                else:
                    current.append(line_obj)

        if current:
            blocks.append(current)

        return blocks

    def _parse_block(self, block: List[Dict]) -> Dict:
        """Extract all detectable fields from a single publication block."""
        entry: Dict[str, Any] = {"confidence": 0.7, "authors": []}

        full_text = "\n".join(line["text"] for line in block)
        first_line = block[0]

        # Title heuristic: the first line (or first sentence) is usually the title.
        title_text = first_line["text"].lstrip("-•*0123456789. ").strip()
        if title_text:
            entry["title"] = self._create_field(title_text, 0.75, first_line)

        for line_obj in block:
            text = line_obj["text"]

            # DOI
            doi_match = self._DOI_PATTERN.search(text)
            if doi_match and not entry.get("doi"):
                entry["doi"] = self._create_field(doi_match.group(0), 0.95, line_obj)

            # URL (prefer DOI over generic URL)
            url_match = self._URL_PATTERN.search(text)
            if url_match and not entry.get("url") and not entry.get("doi"):
                entry["url"] = self._create_field(url_match.group(0), 0.9, line_obj)

            # Year
            year_match = self._YEAR_PATTERN.search(text)
            if year_match and not entry.get("year"):
                entry["year"] = self._create_field(
                    year_match.group(1), 0.9, line_obj
                )

            # Venue (journal / conference name)
            venue_match = self._VENUE_PATTERN.search(text)
            if venue_match and not entry.get("venue"):
                entry["venue"] = self._create_field(
                    text.strip(), 0.75, line_obj
                )

            # Authors: look for comma-separated name patterns
            author_match = self._AUTHOR_PATTERN.search(text)
            if author_match and not entry["authors"]:
                raw_authors = [
                    a.strip()
                    for a in re.split(r",\s*", author_match.group(0))
                    if a.strip()
                ]
                entry["authors"] = [
                    self._create_field(a, 0.7, line_obj)
                    for a in raw_authors
                    if a
                ]

        # Full text as description (useful for unstructured citations)
        entry["description"] = self._create_field(full_text.strip(), 0.8, first_line)

        return entry

"""Generic activity extractor for Leadership, Volunteer Work, and Activities.

A single extractor class handles all three section types because they share
identical structure: an organization, a role, optional dates, and a description.
The ``section_key`` constructor argument carries the semantic context so that
each ``ExtractedField.source.section`` reflects the actual originating section.

Instantiate once per section type in ``EntityExtractionStage``::

    leadership_extractor = GenericActivityExtractor(section_key="leadership")
    volunteer_extractor  = GenericActivityExtractor(section_key="volunteer")
    activity_extractor   = GenericActivityExtractor(section_key="activities")
"""

import re
from typing import Any, Dict, List, Optional


class GenericActivityExtractor:
    """Deterministic extractor for leadership, volunteer, and activity entries.

    Args:
        section_key: The section name (``"leadership"``, ``"volunteer"``,
            or ``"activities"``). Used to populate ``source.section`` on
            every extracted field.
    """

    # Job-title-like patterns commonly seen in leadership and volunteer sections.
    _ROLE_PATTERNS = re.compile(
        r"\b(president|vice president|vp|secretary|treasurer|director|"
        r"coordinator|chair|co-chair|founder|co-founder|lead|head|"
        r"manager|officer|mentor|captain|organizer|volunteer)\b",
        re.IGNORECASE,
    )

    # Common cause/domain keywords — primarily useful for volunteer entries.
    _CAUSE_PATTERNS = re.compile(
        r"\b(education|environment|health|community|literacy|poverty|"
        r"animal welfare|disaster relief|humanitarian|food bank|"
        r"social justice|mental health|youth|elderly|disability)\b",
        re.IGNORECASE,
    )

    # Year (4-digit) and month-year date patterns.
    _DATE_PATTERN = re.compile(
        r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?)\s+\d{4}\b|\b20\d{2}\b|\bpresent\b",
        re.IGNORECASE,
    )

    def __init__(self, section_key: str) -> None:
        self._section_key = section_key

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def extract(self, lines: List[Dict]) -> List[Dict]:
        """Extract structured activity entries from a list of section lines.

        Args:
            lines: Cleaned line objects from ``document.sections[section_key]``.

        Returns:
            A list of raw dicts conforming to ``GenericActivityEntry`` schema.
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
        """Wrap a value in the standard ExtractedField dict structure."""
        if not value:
            return None
        return {
            "value": value,
            "confidence": confidence,
            "source": {
                "page": source_line["page"],
                "section": self._section_key,
                "line": source_line["line_no"],
            },
            "origin_model": "deterministic",
        }

    def _segment_blocks(self, lines: List[Dict]) -> List[List[Dict]]:
        """Split lines into contiguous blocks separated by blank-line gaps."""
        blocks: List[List[Dict]] = []
        current: List[Dict] = []

        for line_obj in lines:
            if not current:
                current.append(line_obj)
            else:
                gap = line_obj["line_no"] - current[-1]["line_no"]
                if gap > 1:
                    blocks.append(current)
                    current = [line_obj]
                else:
                    current.append(line_obj)

        if current:
            blocks.append(current)

        return blocks

    def _parse_block(self, block: List[Dict]) -> Dict:
        """Extract all fields from a single activity block."""
        entry: Dict[str, Any] = {"confidence": 0.75}

        # Heuristic: the first non-bullet line is the org name or role title.
        first_line = block[0]
        first_text = first_line["text"].lstrip("-•* ").strip()
        if first_text:
            entry["organization"] = self._create_field(first_text, 0.75, first_line)

        dates_found: List[str] = []

        for line_obj in block:
            text = line_obj["text"]

            # Role detection — search for leadership/volunteer title keywords.
            role_match = self._ROLE_PATTERNS.search(text)
            if role_match and "role" not in entry:
                entry["role"] = self._create_field(
                    text.lstrip("-•* ").strip(), 0.8, line_obj
                )

            # Cause detection — relevant for volunteer entries.
            cause_match = self._CAUSE_PATTERNS.search(text)
            if cause_match and "cause" not in entry:
                entry["cause"] = self._create_field(
                    cause_match.group(0).strip(), 0.7, line_obj
                )

            # Date extraction
            date_matches = self._DATE_PATTERN.findall(text)
            dates_found.extend(date_matches)

        # Assign start/end dates from the first two date mentions.
        if len(dates_found) >= 1:
            entry["start_date"] = self._create_field(
                dates_found[0], 0.8, block[0]
            )
        if len(dates_found) >= 2:
            entry["end_date"] = self._create_field(
                dates_found[-1], 0.8, block[-1]
            )

        # Full block text as description.
        desc = "\n".join(line["text"] for line in block)
        entry["description"] = self._create_field(desc, 0.85, block[0])

        return entry

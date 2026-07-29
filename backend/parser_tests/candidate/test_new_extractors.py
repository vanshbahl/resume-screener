"""Tests for the new entity extractors: GenericActivityExtractor and PublicationExtractor."""

import pytest

from app.ai.extractors.generic_activity_extractor import GenericActivityExtractor
from app.ai.extractors.publication_extractor import PublicationExtractor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lines(*texts: str, start_line: int = 1) -> list:
    """Build line dicts as they come from the cleaned_lines list."""
    return [
        {"text": t, "page": 1, "line_no": start_line + i}
        for i, t in enumerate(texts)
    ]


# ---------------------------------------------------------------------------
# GenericActivityExtractor — Leadership
# ---------------------------------------------------------------------------

class TestLeadershipExtractor:
    @pytest.fixture
    def extractor(self):
        return GenericActivityExtractor(section_key="leadership")

    def test_empty_lines_returns_empty(self, extractor):
        assert extractor.extract([]) == []

    def test_extracts_organization_from_first_line(self, extractor):
        lines = _lines("Google Developer Student Club", "President", "Aug 2022 – May 2023")
        result = extractor.extract(lines)
        assert len(result) == 1
        assert result[0]["organization"]["value"] == "Google Developer Student Club"

    def test_extracts_role_with_keyword(self, extractor):
        lines = _lines("ACM Chapter", "Chapter President — 2022", "Led 150+ member club")
        result = extractor.extract(lines)
        assert len(result) == 1
        assert "role" in result[0]

    def test_extracts_dates(self, extractor):
        lines = _lines("CS Society", "Co-chair from January 2023 to Present")
        result = extractor.extract(lines)
        assert "start_date" in result[0]

    def test_source_section_is_correct(self, extractor):
        lines = _lines("Tech Club", "Founder")
        result = extractor.extract(lines)
        assert result[0]["organization"]["source"]["section"] == "leadership"

    def test_multiple_blocks_by_line_gap(self, extractor):
        """Two entries separated by a blank line gap should produce two blocks."""
        lines = _lines("Club A", "President", start_line=1)
        lines += _lines("Club B", "Secretary", start_line=10)  # gap > 1
        result = extractor.extract(lines)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# GenericActivityExtractor — Volunteer
# ---------------------------------------------------------------------------

class TestVolunteerExtractor:
    @pytest.fixture
    def extractor(self):
        return GenericActivityExtractor(section_key="volunteer")

    def test_source_section_is_volunteer(self, extractor):
        lines = _lines("Local Food Bank", "Volunteer Coordinator")
        result = extractor.extract(lines)
        assert result[0]["organization"]["source"]["section"] == "volunteer"

    def test_cause_detected(self, extractor):
        lines = _lines("Habitat for Humanity", "Community service — education focus")
        result = extractor.extract(lines)
        assert "cause" in result[0], (
            "A cause keyword should be detected from volunteer section text."
        )
        # The cause value should be a non-empty string
        assert result[0]["cause"]["value"]


# ---------------------------------------------------------------------------
# GenericActivityExtractor — Activities
# ---------------------------------------------------------------------------

class TestActivityExtractor:
    @pytest.fixture
    def extractor(self):
        return GenericActivityExtractor(section_key="activities")

    def test_source_section_is_activities(self, extractor):
        lines = _lines("Photography Club", "Member since 2021")
        result = extractor.extract(lines)
        assert result[0]["organization"]["source"]["section"] == "activities"

    def test_description_always_populated(self, extractor):
        lines = _lines("Hiking Group", "Active participant")
        result = extractor.extract(lines)
        assert result[0]["description"] is not None


# ---------------------------------------------------------------------------
# PublicationExtractor
# ---------------------------------------------------------------------------

class TestPublicationExtractor:
    @pytest.fixture
    def extractor(self):
        return PublicationExtractor()

    def test_empty_lines_returns_empty(self, extractor):
        assert extractor.extract([]) == []

    def test_extracts_doi(self, extractor):
        lines = _lines(
            "Attention Is All You Need",
            "Vaswani et al., 2017. DOI: 10.48550/arXiv.1706.03762"
        )
        result = extractor.extract(lines)
        assert result[0]["doi"]["value"].startswith("10.48550")

    def test_extracts_year(self, extractor):
        lines = _lines("A Survey of NLP Techniques, EMNLP 2022")
        result = extractor.extract(lines)
        assert result[0]["year"]["value"] == "2022"

    def test_extracts_url(self, extractor):
        lines = _lines("My Paper Title", "Available at: https://arxiv.org/abs/2301.00001")
        result = extractor.extract(lines)
        assert "url" in result[0]
        assert result[0]["url"]["value"].startswith("https://")

    def test_extracts_venue_keyword(self, extractor):
        lines = _lines("Deep Learning for Resume Parsing", "Proceedings of ACL 2023")
        result = extractor.extract(lines)
        assert "venue" in result[0]

    def test_title_extracted_from_first_line(self, extractor):
        lines = _lines("Transformer Models for Information Extraction", "arXiv 2023")
        result = extractor.extract(lines)
        assert "Transformer Models" in result[0]["title"]["value"]

    def test_description_always_present(self, extractor):
        lines = _lines("Some paper with no structured info")
        result = extractor.extract(lines)
        assert result[0]["description"] is not None

    def test_multiple_publications_segmented(self, extractor):
        """Publications separated by line gaps should produce multiple entries."""
        pub1 = _lines("Paper One Title", "Journal of AI, 2022", start_line=1)
        pub2 = _lines("Paper Two Title", "ICML 2023", start_line=10)  # gap
        result = extractor.extract(pub1 + pub2)
        assert len(result) == 2

import re
from typing import Any, Dict, List

from app.parsers.core.document import PipelineContext


class EducationExtractor:
    def _create_field(
        self, value: Any, conf: float, source_line: Dict, section: str = "education"
    ) -> Dict:
        if not value:
            return None
        return {
            "value": value,
            "confidence": conf,
            "source": {
                "page": source_line["page"],
                "section": section,
                "line": source_line["line_no"],
            },
            "origin_model": "deterministic",
        }

    def _get_date_pattern(self, context: PipelineContext) -> str:
        date_pattern = (
            context.config.get("date_patterns", {})
            .get("formats", {})
            .get("range_regex", r"")
        )
        if not date_pattern:
            date_pattern = r"((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4})\s*(?:-|to|–|—)\s*((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4}|present|current|now)"
        return date_pattern

    def extract(self, lines: List[Dict], context: PipelineContext) -> List[Dict]:
        if not lines:
            return []

        blocks = []
        current_block = []

        for line_obj in lines:
            if not current_block:
                current_block.append(line_obj)
            else:
                prev = current_block[-1]
                if line_obj["line_no"] - prev["line_no"] > 1:
                    blocks.append(current_block)
                    current_block = [line_obj]
                else:
                    current_block.append(line_obj)
        if current_block:
            blocks.append(current_block)

        parsed_entries = []
        date_pattern = self._get_date_pattern(context)

        for blk in blocks:
            entry = {"confidence": 0.8}

            for line in blk:
                text = line["text"]
                match = re.search(date_pattern, text, re.IGNORECASE)
                if match and "start_date" not in entry:
                    entry["start_date"] = self._create_field(match.group(1), 0.9, line)
                    entry["end_date"] = self._create_field(match.group(2), 0.9, line)

                    # Heuristic for expected graduation
                    if (
                        "expected" in text.lower()
                        or "present" in match.group(2).lower()
                        or "now" in match.group(2).lower()
                    ):
                        entry["expected_graduation"] = self._create_field(
                            match.group(2), 0.85, line
                        )
                    else:
                        entry["graduation_year"] = self._create_field(
                            match.group(2), 0.85, line
                        )

                single_year_match = re.search(r"\b(20\d{2})\b", text)
                if single_year_match and not match and "graduation_year" not in entry:
                    if "expected" in text.lower():
                        entry["expected_graduation"] = self._create_field(
                            single_year_match.group(1), 0.8, line
                        )
                    else:
                        entry["graduation_year"] = self._create_field(
                            single_year_match.group(1), 0.8, line
                        )

                cgpa_match = re.search(
                    r"(?:CGPA|GPA)[\s:]*(\d\.\d+)", text, re.IGNORECASE
                )
                if cgpa_match and "cgpa" not in entry:
                    entry["cgpa"] = self._create_field(cgpa_match.group(1), 0.9, line)

                percentage_match = re.search(r"(\d{2,3}(?:\.\d+)?)\s*%", text)
                if percentage_match and "percentage" not in entry:
                    entry["percentage"] = self._create_field(
                        percentage_match.group(1), 0.9, line
                    )

                semester_match = re.search(
                    r"(\d(?:st|nd|rd|th)\s*semester)", text, re.IGNORECASE
                )
                if semester_match and "current_semester" not in entry:
                    entry["current_semester"] = self._create_field(
                        semester_match.group(1), 0.9, line
                    )

                edu_keywords = [
                    "university",
                    "college",
                    "institute",
                    "school",
                    "academy",
                ]
                if (
                    any(k in text.lower() for k in edu_keywords)
                    and "institution" not in entry
                ):
                    entry["institution"] = self._create_field(text, 0.9, line)

                deg_keywords = [
                    "b.s.",
                    "b.a.",
                    "bachelor",
                    "master",
                    "m.s.",
                    "m.a.",
                    "phd",
                    "ph.d",
                    "degree",
                    "b.tech",
                    "m.tech",
                    "diploma",
                ]
                if (
                    any(k in text.lower() for k in deg_keywords)
                    and "degree" not in entry
                ):
                    # Very simple heuristing: if "in" is present, it might be Degree in Field
                    deg_match = re.search(
                        r"([A-Za-z\.\s]+)\s+in\s+([A-Za-z\s]+)", text, re.IGNORECASE
                    )
                    if deg_match:
                        entry["degree"] = self._create_field(
                            deg_match.group(1).strip(), 0.85, line
                        )
                        entry["field_of_study"] = self._create_field(
                            deg_match.group(2).strip(), 0.85, line
                        )
                    else:
                        entry["degree"] = self._create_field(text, 0.8, line)

                loc_match = re.search(
                    r"([A-Z][a-zA-Z\s]+),\s*([A-Z]{2}|[A-Z][a-zA-Z\s]+)", text
                )
                if (
                    loc_match
                    and "location" not in entry
                    and "university" not in loc_match.group(0).lower()
                ):
                    entry["location"] = self._create_field(
                        loc_match.group(0), 0.8, line
                    )

            desc_text = "\n".join([l["text"] for l in blk])
            entry["description"] = self._create_field(desc_text, 0.9, blk[0])

            parsed_entries.append(entry)

        return parsed_entries

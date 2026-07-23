import re
from typing import Any, Dict, List


class AchievementExtractor:
    def _create_field(
        self, value: Any, conf: float, source_line: Dict, section: str = "achievements"
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

    def extract(self, lines: List[Dict]) -> List[Dict]:
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

        parsed = []
        for blk in blocks:
            entry = {"confidence": 0.8}

            for line in blk:
                text = line["text"]

                rank_match = re.search(
                    r"\b(1st|2nd|3rd|4th|[0-9]+th|winner|runner up|finalist)\b",
                    text,
                    re.IGNORECASE,
                )
                if rank_match and "rank" not in entry:
                    entry["rank"] = self._create_field(rank_match.group(1), 0.9, line)

                award_match = re.search(
                    r"\b(award|prize|scholarship|medal|honorable mention)\b",
                    text,
                    re.IGNORECASE,
                )
                if award_match and "award" not in entry:
                    entry["award"] = self._create_field(
                        text, 0.7, line
                    )  # the whole text might be the award name

                comp_match = re.search(
                    r"\b(hackathon|competition|olympiad|championship|tournament)\b",
                    text,
                    re.IGNORECASE,
                )
                if comp_match and "competition" not in entry:
                    entry["competition"] = self._create_field(text, 0.7, line)

                year_match = re.search(r"\b(20\d{2})\b", text)
                if year_match and "year" not in entry:
                    entry["year"] = self._create_field(year_match.group(1), 0.9, line)

            desc_text = "\n".join([l["text"] for l in blk])
            entry["description"] = self._create_field(desc_text, 0.9, blk[0])
            parsed.append(entry)

        return parsed

import re
from typing import List, Dict, Any
from app.parsers.core.document import PipelineContext


class ProjectExtractor:
    def __init__(self):
        from app.ai.extractors.skills_extractor import SkillsExtractor
        self.skills_extractor = SkillsExtractor()

        # A project name line is typically:
        # - Short (< 80 chars)
        # - NOT a bullet point
        # - NOT a tech stack line ("Stack:", "Technologies:", or starts with comma-separated terms)
        # - NOT a long description sentence
        # - Does NOT start with a lowercase letter (descriptions often do)
        self._stack_prefix = re.compile(
            r'^(stack|tech|technologies|tools|built with|tech stack)\s*:', re.IGNORECASE
        )
        self._role_duration = re.compile(
            r'\b(ongoing|lead developer|team leader|developer|contributor)\b', re.IGNORECASE
        )

    def _create_field(self, value: Any, conf: float, source_line: Dict, section: str = "projects") -> Dict:
        if not value:
            return None
        return {
            "value": value,
            "confidence": conf,
            "source": {
                "page": source_line["page"],
                "section": section,
                "line": source_line["line_no"]
            },
            "origin_model": "deterministic"
        }

    def _is_project_name(self, text: str) -> bool:
        """Heuristic: is this line a project name / new project boundary?"""
        stripped = text.strip()
        if not stripped:
            return False
        # Bullet points are NOT project names
        if stripped.startswith(("-", "•", "*", "·")):
            return False
        # Stack lines are NOT project names
        if self._stack_prefix.match(stripped):
            return False
        # Long sentences (> 80 chars) are descriptions
        if len(stripped) > 80:
            return False
        # Lines starting with lowercase are likely continuation sentences
        if stripped[0].islower():
            return False
        # Lines that are purely a year or short number are not names
        if re.match(r'^\d{4}$', stripped):
            return False
        # Role/duration summary lines ("Ongoing · Lead Developer") are NOT project names
        if self._role_duration.search(stripped):
            return False
        # Achievement/recognition lines are NOT project names
        if re.search(
            r'\b(shortlisted|finalist|participant|winner|runner.up|place at|place in|'
            r'hackathon|pitchcraft|presented at|codex)\b',
            stripped, re.IGNORECASE
        ):
            return False
        # Lines that start with "I " or "H " or single-letter prefix are PDF extraction artifacts
        if re.match(r'^[A-Z]\s+\d', stripped):
            return False
        return True

    def _split_into_blocks(self, lines: List[Dict]) -> List[List[Dict]]:
        """
        Split project lines into individual project blocks using two strategies:
        1. line_no gaps > 1 (PDF had blank lines between projects)
        2. Heuristic name detection: a line that looks like a new project name
           after the block has already accumulated at least one non-name line.
        """
        blocks = []
        current_block = []

        for line_obj in lines:
            text = line_obj["text"]

            if not current_block:
                current_block.append(line_obj)
                continue

            prev = current_block[-1]

            # Strategy 1: blank-line gap in raw PDF (line_no sparse)
            if line_obj["line_no"] - prev["line_no"] > 1:
                blocks.append(current_block)
                current_block = [line_obj]
                continue

            # Strategy 2: heuristic name boundary
            # A new project starts if: this line looks like a project name AND
            # the current block has accumulated at least 1 non-name line already.
            block_has_content = any(
                not self._is_project_name(l["text"]) for l in current_block
            )
            if block_has_content and self._is_project_name(text):
                blocks.append(current_block)
                current_block = [line_obj]
                continue

            current_block.append(line_obj)

        if current_block:
            blocks.append(current_block)

        return blocks

    def extract(self, lines: List[Dict], context: PipelineContext) -> List[Dict]:
        if not lines:
            return []

        blocks = self._split_into_blocks(lines)
        parsed_entries = []

        for blk in blocks:
            entry = {"confidence": 0.8, "awards": []}

            # First line is typically the project name
            if blk:
                name_text = blk[0]["text"].strip().lstrip("-•* ")
                entry["name"] = self._create_field(name_text, 0.9, blk[0])

            for line in blk:
                text = line["text"]

                # Full URL regex: captures scheme + host + path + query
                link_match = re.search(
                    r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}'
                    r'(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
                    text
                )
                if link_match and "link" not in entry:
                    entry["link"] = self._create_field(link_match.group(0), 0.9, line)

                dur_match = re.search(r'(?:duration|timeline):\s*(.*)', text, re.IGNORECASE)
                if dur_match and "duration" not in entry:
                    entry["duration"] = self._create_field(dur_match.group(1), 0.9, line)

                # Extract inline role/duration markers like "Ongoing · Lead Developer"
                if self._role_duration.search(text) and "role" not in entry:
                    role_val = text.strip().lstrip("·- ")
                    entry["role"] = self._create_field(role_val, 0.85, line)

                award_match = re.search(
                    r'(?:winner|1st|2nd|3rd|prize|hackathon|shortlisted|finalist)', text, re.IGNORECASE
                )
                if award_match and len(text) < 120:
                    entry["awards"].append(self._create_field(text, 0.8, line))

            skills_dict = self.skills_extractor.extract(blk, context)
            entry["technologies"] = skills_dict.get("skills", [])

            desc_text = "\n".join([l["text"] for l in blk])
            entry["description"] = self._create_field(desc_text, 0.9, blk[0])

            parsed_entries.append(entry)

        return parsed_entries

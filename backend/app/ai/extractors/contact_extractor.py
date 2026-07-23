import re
from typing import List, Dict, Optional, Any


class ContactExtractor:
    def __init__(self):
        self.email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        # Phone: handles US (3+3+4), Indian (+91 5+5), UK (4+6), and general intl formats
        self.phone_regex = re.compile(
            r'(\+?\d{1,3}[\s\-.]?)?' # optional country code
            r'(?:\(?\d{2,5}\)?[\s\-.]?)' # area code (2-5 digits)
            r'\d{3,5}[\s\-.]?' # middle digits
            r'\d{3,5}' # last digits
        )
        # Capture profile path only (host + /username)
        self.linkedin_regex = re.compile(
            r'(https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-]+/?',
            re.IGNORECASE
        )
        # Capture profile path only (host + /username) — NOT repo sub-paths
        self.github_regex = re.compile(
            r'(https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_\-]+/?',
            re.IGNORECASE
        )
        # Full URL with path for portfolio/website detection
        self.url_regex = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}'
            r'(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        )
        # Bare hostname without scheme: e.g. myportfolio.com, johndoe.dev
        # Requires: 3+ chars before dot, known web TLD, 6+ total chars
        self.bare_host_regex = re.compile(
            r'(?<![/@\w])([a-zA-Z0-9][a-zA-Z0-9\-]{2,}(?:\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,6}(?:/[-a-zA-Z0-9@:%_\+.~#?&/=]*)?)(?![\w])'
        )
        self.location_regex = re.compile(r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2}|[A-Z][a-zA-Z\s]+)')

    def _create_field(self, value: Any, conf: float, source_line: Dict, section: str = "personal_info") -> Dict:
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

    def extract(self, lines: List[Dict]) -> Dict:
        """
        Extracts contact information from section lines.
        Handles full URLs, bare hostnames, and all standard contact fields.
        """
        result = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "portfolio": None,
            "website": None,
            "location": None
        }

        # Name heuristic: first 1-4 word line (no contact markers) in the first 5 lines
        for line_obj in lines[:5]:
            text = line_obj["text"]
            if self.email_regex.search(text) or self.phone_regex.search(text):
                continue
            if "http" in text.lower() or "www" in text.lower() or "@" in text:
                continue
            if re.match(r'^[A-Za-z\- \.]{2,50}$', text):
                words = text.split()
                if 1 < len(words) <= 4:
                    result["name"] = self._create_field(
                        text.title() if text.isupper() else text, 0.9, line_obj
                    )
                    break

        for line_obj in lines:
            text = line_obj["text"]

            if not result["email"]:
                match = self.email_regex.search(text)
                if match:
                    result["email"] = self._create_field(match.group(0), 1.0, line_obj)

            if not result["phone"]:
                match = self.phone_regex.search(text)
                if match:
                    result["phone"] = self._create_field(match.group(0).strip(), 0.95, line_obj)

            if not result["linkedin"]:
                match = self.linkedin_regex.search(text)
                if match:
                    result["linkedin"] = self._create_field(
                        match.group(0).rstrip("/"), 1.0, line_obj
                    )

            if not result["github"]:
                match = self.github_regex.search(text)
                if match:
                    result["github"] = self._create_field(
                        match.group(0).rstrip("/"), 1.0, line_obj
                    )

            # Full schemed URLs: portfolio/website (excluding known social platforms)
            for url in self.url_regex.findall(text):
                url_lower = url.lower()
                if "linkedin.com" in url_lower or "github.com" in url_lower:
                    continue
                if not result["portfolio"]:
                    result["portfolio"] = self._create_field(url, 0.9, line_obj)

            # Bare hostnames (no https://) for portfolio
            if not result["portfolio"]:
                # Known tech library/framework names that look like hostnames
                tech_false_positives = {
                    "socket.io", "mongoose.js", "socket.io", "tailwind.css",
                    "radix.ui", "lucide.dev", "supabase.io", "nodemailer.io",
                    "sqlalchemy.org", "jwt.io", "vite.dev", "next.js", "node.js",
                    "react.js", "vue.js", "express.js", "angular.js"
                }
                for match in self.bare_host_regex.finditer(text):
                    candidate = match.group(1)
                    if not candidate or len(candidate) < 6:
                        continue
                    cand_lower = candidate.lower()
                    # Exclude known social platforms and tech library false positives
                    if any(p in cand_lower for p in ["github.com", "linkedin.com", "twitter.com", "instagram.com"]):
                        continue
                    if cand_lower in tech_false_positives:
                        continue
                    if "@" in candidate:
                        continue
                    # Must end with a real web TLD
                    if not re.search(r'\.(com|io|dev|net|org|me|co|in|app|tech|xyz|ai)(/|$)', candidate, re.IGNORECASE):
                        continue
                    # Exclude short abbreviations: first part must be 3+ chars
                    first_part = candidate.split(".")[0]
                    if len(first_part) < 3:
                        continue
                    # Exclude lines that look like tech stack declarations
                    # (the bare host appears inside a comma-separated tech list)
                    if text.count(",") > 2 and len(text) > 40:
                        continue
                    result["portfolio"] = self._create_field(candidate, 0.8, line_obj)
                    break

            if not result["location"]:
                match = self.location_regex.search(text)
                if match and "university" not in match.group(0).lower():
                    result["location"] = self._create_field(match.group(0), 0.8, line_obj)

        return result

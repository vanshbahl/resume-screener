import re
from typing import List, Dict, Optional, Any
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import ResumeDocument, PipelineContext

class EntityExtractionStage(BaseParserStage):
    def run(self, document: ResumeDocument, context: PipelineContext) -> None:
        pi_section = document.sections.get("personal_info", {"lines": []})
        pi_lines = pi_section.get("lines", [])
        
        extracted = {
            "personal_info": {
                "name": self.extract_name(pi_lines, "personal_info", context),
                "email": self.extract_email(pi_lines, "personal_info"),
                "phone": self.extract_phone(pi_lines, "personal_info"),
                "location": None
            },
            "summary": None,
            "skills": self.extract_flat_skills(document.sections.get("skills", {}).get("lines", []), "skills"),
            "education": self.parse_nested_blocks(document.sections.get("education", {}).get("lines", []), "education"),
            "experience": self.parse_nested_blocks(document.sections.get("experience", {}).get("lines", []), "experience"),
            "projects": self.parse_nested_blocks(document.sections.get("projects", {}).get("lines", []), "projects"),
            "certifications": self.parse_nested_blocks(document.sections.get("certifications", {}).get("lines", []), "certifications"),
            "achievements": self.parse_nested_blocks(document.sections.get("achievements", {}).get("lines", []), "achievements"),
            "languages": self.extract_flat_skills(document.sections.get("languages", {}).get("lines", []), "languages")
        }
        
        links = self.extract_links(pi_lines, "personal_info")
        extracted["personal_info"].update(links)
        
        summary_lines = document.sections.get("summary", {}).get("lines", [])
        if summary_lines:
            desc = "\n".join(x["text"] for x in summary_lines)
            extracted["summary"] = self.create_field(desc, 0.9, summary_lines[0], "summary")
            
        document.extracted_entities = extracted

    def create_field(self, value: Any, conf: float, source_line: Dict, section: str) -> Dict:
        if value is None: return None
        return {
            "value": value,
            "confidence": conf,
            "source": {
                "page": source_line["page"],
                "section": section,
                "line": source_line["line_no"]
            }
        }

    def extract_email(self, lines: List[Dict], section: str) -> Optional[Dict]:
        for line_obj in lines:
            match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line_obj["text"])
            if match: return self.create_field(match.group(0), 1.0, line_obj, section)
        return None

    def extract_phone(self, lines: List[Dict], section: str) -> Optional[Dict]:
        for line_obj in lines:
            match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line_obj["text"])
            if match: return self.create_field(match.group(0), 0.95, line_obj, section)
        return None

    def extract_links(self, lines: List[Dict], section: str) -> Dict[str, Optional[Dict]]:
        links = {"linkedin": None, "github": None, "portfolio": None}
        for line_obj in lines:
            text = line_obj["text"]
            linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?', text)
            if linkedin_match and not links["linkedin"]: 
                links["linkedin"] = self.create_field(linkedin_match.group(0), 1.0, line_obj, section)
                
            github_match = re.search(r'(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+/?', text)
            if github_match and not links["github"]: 
                links["github"] = self.create_field(github_match.group(0), 1.0, line_obj, section)
                
            url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
            urls = re.findall(url_pattern, text)
            for url in urls:
                if "linkedin.com" not in url and "github.com" not in url:
                    if not links["portfolio"]:
                        links["portfolio"] = self.create_field(url, 0.8, line_obj, section)
                    break
        return links

    def extract_name(self, lines: List[Dict], section: str, context: PipelineContext) -> Optional[Dict]:
        for line_obj in lines[:3]: 
            text = line_obj["text"]
            if self.extract_email([line_obj], section) or self.extract_phone([line_obj], section) or "http" in text or "www" in text:
                continue
            if re.match(r'^[A-Za-z\- \.]{2,40}$', text):
                words = text.split()
                if 1 < len(words) <= 4:
                    return self.create_field(text, 0.85, line_obj, section)
                    
        context.log_warning("LowConfidenceName", "Could not heuristically extract a confident name.")
        return None

    def extract_flat_skills(self, lines: List[Dict], section: str) -> List[Dict]:
        skills = []
        seen = set()
        for line_obj in lines:
            items = re.split(r'[,\n]', line_obj["text"])
            for item in items:
                cleaned = item.strip().strip('-•* ')
                if cleaned and len(cleaned) < 40 and cleaned.lower() not in seen: 
                    seen.add(cleaned.lower())
                    skills.append(self.create_field(cleaned, 0.9, line_obj, section))
        return skills

    def parse_nested_blocks(self, lines: List[Dict], section: str) -> List[Dict]:
        if not lines: return []
        
        blocks = []
        current_block = []
        
        for i, line_obj in enumerate(lines):
            if not current_block:
                current_block.append(line_obj)
            else:
                prev = current_block[-1]
                if line_obj["line_no"] - prev["line_no"] > 1:
                    desc_text = "\n".join(x["text"] for x in current_block)
                    blocks.append({
                        "description": self.create_field(desc_text, 0.5, current_block[0], section),
                        "confidence": 0.5
                    })
                    current_block = [line_obj]
                else:
                    current_block.append(line_obj)
                    
        if current_block:
            desc_text = "\n".join(x["text"] for x in current_block)
            blocks.append({
                "description": self.create_field(desc_text, 0.5, current_block[0], section),
                "confidence": 0.5
            })
            
        return blocks

import re
from typing import List, Dict, Optional, Any
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import ResumeDocument, PipelineContext

class EntityExtractionStage(BaseParserStage):
    def run(self, document: ResumeDocument, context: PipelineContext) -> None:
        pi_section = document.sections.get("personal_info", {"lines": []})
        pi_lines = pi_section.get("lines", [])
        
        skills_dict = self.parse_skills_section(document.sections.get("skills", {}).get("lines", []), context)
        
        extracted = {
            "personal_info": {
                "name": self.extract_name(pi_lines, "personal_info", context),
                "email": self.extract_email(pi_lines, "personal_info"),
                "phone": self.extract_phone(pi_lines, "personal_info"),
                "location": self.extract_location(pi_lines, "personal_info")
            },
            "summary": None,
            "skills": skills_dict.get("skills", []),
            "languages": skills_dict.get("languages", []),
            "frameworks": skills_dict.get("frameworks", []),
            "tools": skills_dict.get("tools", []) + skills_dict.get("databases", []),
            "concepts": skills_dict.get("concepts", []),
            "soft_skills": skills_dict.get("soft_skills", []),
            "education": self.parse_education_blocks(document.sections.get("education", {}).get("lines", []), "education", context),
            "experience": self.parse_experience_blocks(document.sections.get("experience", {}).get("lines", []), "experience", context),
            "projects": self.parse_project_blocks(document.sections.get("projects", {}).get("lines", []), "projects", context),
            "certifications": self.parse_generic_blocks(document.sections.get("certifications", {}).get("lines", []), "certifications"),
            "achievements": self.parse_generic_blocks(document.sections.get("achievements", {}).get("lines", []), "achievements")
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
        
    def extract_location(self, lines: List[Dict], section: str) -> Optional[Dict]:
        for line_obj in lines:
            # Simple heuristic: City, State or City, Country
            match = re.search(r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2}|[A-Z][a-zA-Z\s]+)', line_obj["text"])
            if match and "university" not in match.group(0).lower(): 
                return self.create_field(match.group(0), 0.8, line_obj, section)
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
        for line_obj in lines[:5]: 
            text = line_obj["text"]
            if self.extract_email([line_obj], section) or self.extract_phone([line_obj], section) or "http" in text or "www" in text:
                continue
            if re.match(r'^[A-Za-z\- \.]{2,40}$', text):
                words = text.split()
                if 1 < len(words) <= 4:
                    return self.create_field(text.title() if text.isupper() else text, 0.9, line_obj, section)
                    
        context.log_warning("LowConfidenceName", "Could not heuristically extract a confident name.")
        return None

    def parse_skills_section(self, lines: List[Dict], context: PipelineContext) -> Dict[str, List[Dict]]:
        categories = context.config.get("skill_categories", {})
        result = {
            "skills": [], "languages": [], "frameworks": [], 
            "tools": [], "databases": [], "concepts": [], "soft_skills": []
        }
        
        current_cat = "skills"
        seen = set()
        
        for line_obj in lines:
            text = line_obj["text"]
            
            # Check if this line is a category header
            is_cat = False
            for cat_name, pattern in categories.items():
                if re.match(pattern, text.lower().strip(':')):
                    current_cat = cat_name
                    is_cat = True
                    break
            
            # Alternatively, if it looks like "Languages: Python, Go"
            if not is_cat and ":" in text:
                parts = text.split(":", 1)
                header = parts[0].strip().lower()
                for cat_name, pattern in categories.items():
                    if re.match(pattern, header):
                        current_cat = cat_name
                        break
                text = parts[1]
                
            if is_cat:
                continue
                
            items = re.split(r'[,\n]', text)
            for item in items:
                cleaned = item.strip().strip('-•* ')
                if cleaned and len(cleaned) < 40 and cleaned.lower() not in seen: 
                    seen.add(cleaned.lower())
                    result[current_cat].append(self.create_field(cleaned, 0.9, line_obj, "skills"))
                    
        return result

    def get_date_pattern(self, context: PipelineContext) -> str:
        date_pattern = context.config.get("date_patterns", {}).get("formats", {}).get("range_regex", r"")
        if not date_pattern:
            date_pattern = r"((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4})\s*(?:-|to|–|—)\s*((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4}|present|current|now)"
        return date_pattern

    def parse_experience_blocks(self, lines: List[Dict], section: str, context: PipelineContext) -> List[Dict]:
        if not lines: return []
        blocks = []
        current_block = []
        date_pattern = self.get_date_pattern(context)
        
        def process_block(blk: List[Dict]) -> Dict:
            entry = {"confidence": 0.8}
            desc_lines = []
            
            for line in blk:
                text = line["text"]
                match = re.search(date_pattern, text, re.IGNORECASE)
                if match and "start_date" not in entry:
                    entry["start_date"] = self.create_field(match.group(1), 0.9, line, section)
                    entry["end_date"] = self.create_field(match.group(2), 0.9, line, section)
                
                # Check for location
                loc_match = re.search(r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})', text)
                if loc_match and "location" not in entry:
                    entry["location"] = self.create_field(loc_match.group(0), 0.8, line, section)
            
            title_keywords = ["engineer", "developer", "manager", "director", "lead", "analyst", "consultant", "scientist"]
            for i, line in enumerate(blk[:3]):
                text = line["text"]
                if any(k in text.lower() for k in title_keywords):
                    entry["title"] = self.create_field(text, 0.8, line, section)
                elif "company" not in entry and not re.search(date_pattern, text, re.IGNORECASE):
                    entry["company"] = self.create_field(text, 0.7, line, section)
            
            desc_text = "\n".join([l["text"] for l in blk])
            entry["description"] = self.create_field(desc_text, 0.9, blk[0], section)
            return entry

        for line_obj in lines:
            if not current_block:
                current_block.append(line_obj)
            else:
                prev = current_block[-1]
                # Split on double newline
                if line_obj["line_no"] - prev["line_no"] > 1:
                    blocks.append(process_block(current_block))
                    current_block = [line_obj]
                else:
                    current_block.append(line_obj)
                    
        if current_block:
            blocks.append(process_block(current_block))
            
        return blocks

    def parse_education_blocks(self, lines: List[Dict], section: str, context: PipelineContext) -> List[Dict]:
        if not lines: return []
        blocks = []
        current_block = []
        date_pattern = self.get_date_pattern(context)
        
        def process_block(blk: List[Dict]) -> Dict:
            entry = {"confidence": 0.8}
            
            for line in blk:
                text = line["text"]
                match = re.search(date_pattern, text, re.IGNORECASE)
                if match and "start_date" not in entry:
                    entry["start_date"] = self.create_field(match.group(1), 0.9, line, section)
                    entry["end_date"] = self.create_field(match.group(2), 0.9, line, section)
                
                cgpa_match = re.search(r'(?:CGPA|GPA)[\s:]*(\d\.\d+)', text, re.IGNORECASE)
                if cgpa_match and "cgpa" not in entry:
                    entry["cgpa"] = self.create_field(cgpa_match.group(1), 0.9, line, section)
                
                edu_keywords = ["university", "college", "institute"]
                if any(k in text.lower() for k in edu_keywords) and "institution" not in entry:
                    entry["institution"] = self.create_field(text, 0.9, line, section)
                    
                deg_keywords = ["b.s.", "bachelor", "master", "phd", "m.s.", "degree"]
                if any(k in text.lower() for k in deg_keywords) and "degree" not in entry:
                    entry["degree"] = self.create_field(text, 0.9, line, section)
            
            desc_text = "\n".join([l["text"] for l in blk])
            entry["description"] = self.create_field(desc_text, 0.9, blk[0], section)
            return entry

        for line_obj in lines:
            if not current_block:
                current_block.append(line_obj)
            else:
                prev = current_block[-1]
                if line_obj["line_no"] - prev["line_no"] > 1:
                    blocks.append(process_block(current_block))
                    current_block = [line_obj]
                else:
                    current_block.append(line_obj)
                    
        if current_block:
            blocks.append(process_block(current_block))
            
        return blocks

    def parse_project_blocks(self, lines: List[Dict], section: str, context: PipelineContext) -> List[Dict]:
        if not lines: return []
        blocks = []
        current_block = []
        
        def process_block(blk: List[Dict]) -> Dict:
            entry = {"confidence": 0.8}
            
            # The first line is usually the project name
            if blk:
                entry["name"] = self.create_field(blk[0]["text"], 0.8, blk[0], section)
                
            for line in blk:
                text = line["text"]
                link_match = re.search(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b', text)
                if link_match and "link" not in entry:
                    entry["link"] = self.create_field(link_match.group(0), 0.9, line, section)
                    
                dur_match = re.search(r'duration:\s*(.*)', text, re.IGNORECASE)
                if dur_match and "duration" not in entry:
                    entry["duration"] = self.create_field(dur_match.group(1), 0.9, line, section)
            
            desc_text = "\n".join([l["text"] for l in blk])
            entry["description"] = self.create_field(desc_text, 0.9, blk[0], section)
            return entry

        for line_obj in lines:
            if not current_block:
                current_block.append(line_obj)
            else:
                prev = current_block[-1]
                if line_obj["line_no"] - prev["line_no"] > 1:
                    blocks.append(process_block(current_block))
                    current_block = [line_obj]
                else:
                    current_block.append(line_obj)
                    
        if current_block:
            blocks.append(process_block(current_block))
            
        return blocks

    def parse_generic_blocks(self, lines: List[Dict], section: str) -> List[Dict]:
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

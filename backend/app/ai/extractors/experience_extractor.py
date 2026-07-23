import re
from typing import List, Dict, Any
from app.parsers.core.document import PipelineContext

class ExperienceExtractor:
    def __init__(self):
        # We will reuse the SkillsExtractor logic for skills_used
        from app.ai.extractors.skills_extractor import SkillsExtractor
        self.skills_extractor = SkillsExtractor()
        
    def _create_field(self, value: Any, conf: float, source_line: Dict, section: str = "experience") -> Dict:
        if not value: return None
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

    def _get_date_pattern(self, context: PipelineContext) -> str:
        date_pattern = context.config.get("date_patterns", {}).get("formats", {}).get("range_regex", r"")
        if not date_pattern:
            date_pattern = r"((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4})\s*(?:-|to|–|—)\s*((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4}|present|current|now)"
        return date_pattern

    def extract(self, lines: List[Dict], context: PipelineContext) -> List[Dict]:
        if not lines: return []
        
        blocks = []
        current_block = []
        
        # Heuristic 1: Double newline split
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
            
        # Optional Heuristic 2: If a block has multiple date ranges, split it further
        # Skipping for now to keep it deterministic and simple on double newline
        
        parsed_entries = []
        date_pattern = self._get_date_pattern(context)
        title_keywords = ["engineer", "developer", "manager", "director", "lead", "analyst", "consultant", "scientist", "architect", "intern"]
        emp_type_keywords = ["full-time", "part-time", "contract", "freelance", "internship"]

        for blk in blocks:
            entry = {"confidence": 0.8}
            responsibilities = []
            
            for i, line in enumerate(blk):
                text = line["text"]
                
                # Check Dates
                match = re.search(date_pattern, text, re.IGNORECASE)
                if match and "start_date" not in entry:
                    entry["start_date"] = self._create_field(match.group(1), 0.95, line)
                    entry["end_date"] = self._create_field(match.group(2), 0.95, line)
                    
                    # See if duration is explicitly stated like "(3 years)"
                    dur_match = re.search(r'\((.*?(?:year|month).*?)\)', text, re.IGNORECASE)
                    if dur_match:
                        entry["duration"] = self._create_field(dur_match.group(1), 0.9, line)
                
                # Check Location
                loc_match = re.search(r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2}|[A-Z][a-zA-Z\s]+)', text)
                if loc_match and "location" not in entry and not match: 
                    entry["location"] = self._create_field(loc_match.group(0), 0.8, line)
                    
                # Employment Type
                for et in emp_type_keywords:
                    if et in text.lower() and "employment_type" not in entry:
                        entry["employment_type"] = self._create_field(et.title(), 0.9, line)
                        
                # Bullets = responsibilities
                if text.strip().startswith("-") or text.strip().startswith("•") or text.strip().startswith("*"):
                    responsibilities.append(self._create_field(text.strip().lstrip('-•* '), 0.9, line))
                elif i > 0 and len(text) > 80: # long text is likely a responsibility
                    responsibilities.append(self._create_field(text.strip(), 0.8, line))
            
            # Title & Company Heuristics on the first 3 lines
            for i, line in enumerate(blk[:3]):
                text = line["text"]
                # Skip if it's the date line
                if re.search(date_pattern, text, re.IGNORECASE): continue
                
                if any(k in text.lower() for k in title_keywords) and "title" not in entry:
                    entry["title"] = self._create_field(text, 0.9, line)
                elif "company" not in entry and not text.strip().startswith("-"):
                    entry["company"] = self._create_field(text, 0.7, line) # Confidence lower, let AI fusion fix this if needed
                    
            entry["responsibilities"] = responsibilities
            
            # Use SkillsExtractor to find skills used in this job
            skills_dict = self.skills_extractor.extract(blk, context)
            entry["skills_used"] = skills_dict.get("skills", [])
            
            desc_text = "\n".join([l["text"] for l in blk])
            entry["description"] = self._create_field(desc_text, 0.9, blk[0])
            
            parsed_entries.append(entry)
            
        return parsed_entries

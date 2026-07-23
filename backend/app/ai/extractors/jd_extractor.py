import re
from typing import Dict, List, Any
import yaml
import os

class JDExtractor:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), '../../../config/jd_patterns.yaml')
        self.patterns = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.patterns = yaml.safe_load(f) or {}
                
    def _create_field(self, value: Any, source: dict) -> dict:
        return {
            "value": value,
            "confidence": 0.9,
            "origin_model": "deterministic",
            "source": source
        }

    def extract(self, cleaned_lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        result = {
            "salary": None,
            "employment_type": None,
            "location_type": None,
            "degree_requirements": [],
            "visa_requirements": [],
            "experience_requirements": None
        }
        
        full_text = " ".join(l["text"] for l in cleaned_lines).lower()
        first_line_source = None
        if cleaned_lines:
            first_line_source = {
                "page": cleaned_lines[0].get("page", 1),
                "section": "jd_metadata",
                "line": cleaned_lines[0].get("line_no", 1)
            }
            
        # Experience
        exp_cfg = self.patterns.get("experience", {})
        if exp_cfg and "pattern" in exp_cfg:
            match = re.search(exp_cfg["pattern"], full_text)
            if match:
                result["experience_requirements"] = self._create_field(match.group(0), first_line_source)
                
        # Salary
        sal_cfg = self.patterns.get("salary", {})
        if sal_cfg and "pattern" in sal_cfg:
            match = re.search(sal_cfg["pattern"], full_text)
            if match:
                result["salary"] = self._create_field(match.group(0), first_line_source)
                
        # Employment Type
        emp_cfg = self.patterns.get("employment_type", {})
        if emp_cfg and "patterns" in emp_cfg:
            for pat in emp_cfg["patterns"]:
                if re.search(r'\b' + pat + r'\b', full_text):
                    result["employment_type"] = self._create_field(pat.replace("\\", ""), first_line_source)
                    break
                    
        # Location Type
        loc_cfg = self.patterns.get("location_type", {})
        if loc_cfg and "patterns" in loc_cfg:
            for pat in loc_cfg["patterns"]:
                if re.search(r'\b' + pat + r'\b', full_text):
                    result["location_type"] = self._create_field(pat.replace("\\", ""), first_line_source)
                    break
                    
        # Degree
        deg_cfg = self.patterns.get("degree_requirements", {})
        if deg_cfg and "patterns" in deg_cfg:
            for pat in deg_cfg["patterns"]:
                if re.search(r'\b' + pat + r'\b', full_text):
                    result["degree_requirements"].append(self._create_field(pat.replace("\\", "").replace("?", ""), first_line_source))
                    
        # Visa
        visa_cfg = self.patterns.get("visa", {})
        if visa_cfg and "patterns" in visa_cfg:
            for pat in visa_cfg["patterns"]:
                if re.search(r'\b' + pat + r'\b', full_text):
                    result["visa_requirements"].append(self._create_field(pat.replace("\\", ""), first_line_source))
                    
        return result

import re
from typing import List, Dict, Any
from app.parsers.core.document import PipelineContext

class SkillsExtractor:
    def _create_field(self, value: Any, conf: float, source_line: Dict, section: str = "skills") -> Dict:
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

    def extract(self, lines: List[Dict], context: PipelineContext) -> Dict[str, List[Dict]]:
        kb = context.config.get("skills_kb", {})
        
        result = {
            "skills": [],
            "languages": [],
            "frameworks": [],
            "tools": [],
            "concepts": [],
            "soft_skills": []
        }
        
        seen_normalized = set()
        
        # Mapping YAML categories to schema categories
        category_map = {
            "languages": "languages",
            "frameworks": "frameworks",
            "libraries": "frameworks", # Map libraries to frameworks in schema
            "databases": "tools", # Map DBs to tools
            "cloud": "tools",
            "devops": "tools",
            "tools": "tools",
            "concepts": "concepts",
            "soft_skills": "soft_skills"
        }
        
        # Build optimized regex dictionary
        kb_regexes = {}
        for cat, items in kb.items():
            schema_cat = category_map.get(cat, "skills")
            for normalized, aliases in items.items():
                # Escape aliases and sort by length descending to match longest first
                sorted_aliases = sorted(aliases, key=len, reverse=True)
                pattern_str = r'\b(?:' + '|'.join(re.escape(a) for a in sorted_aliases) + r')\b'
                # For special chars like C++, C#, .NET we need to be careful with word boundaries
                # A custom boundary might be needed if they start/end with non-word chars
                custom_patterns = []
                for a in sorted_aliases:
                    prefix = r'(?<![a-zA-Z0-9])' if not a[0].isalnum() else r'\b'
                    suffix = r'(?![a-zA-Z0-9])' if not a[-1].isalnum() else r'\b'
                    custom_patterns.append(prefix + re.escape(a) + suffix)
                
                final_pattern = r'(?:' + '|'.join(custom_patterns) + r')'
                kb_regexes[(schema_cat, normalized)] = re.compile(final_pattern, re.IGNORECASE)
                
        for line_obj in lines:
            text = line_obj["text"]
            for (schema_cat, normalized), regex in kb_regexes.items():
                if normalized in seen_normalized:
                    continue
                    
                match = regex.search(text)
                if match:
                    seen_normalized.add(normalized)
                    result[schema_cat].append(self._create_field(normalized, 0.95, line_obj))
                    result["skills"].append(self._create_field(normalized, 0.95, line_obj)) # Also add to generic skills pool
                    
        return result

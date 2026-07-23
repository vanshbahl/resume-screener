import re
from typing import List, Dict, Any

class LanguageExtractor:
    def _create_field(self, value: Any, conf: float, source_line: Dict, section: str = "languages") -> Dict:
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

    def extract(self, lines: List[Dict]) -> List[Dict]:
        if not lines: return []
        
        # Usually languages are listed in one or two lines like: "English (Native), Spanish (Fluent)"
        # Or a bulleted list.
        parsed = []
        
        fluency_keywords = ["native", "fluent", "proficient", "intermediate", "beginner", "conversational", "bilingual"]
        
        for line in lines:
            text = line["text"]
            # Split by comma or newline
            parts = re.split(r'[,\n]', text)
            for part in parts:
                cleaned = part.strip().lstrip("-•* ")
                if not cleaned or len(cleaned) > 50:
                    continue
                    
                # Search for fluency in the part
                fluency = None
                lang_name = cleaned
                for f in fluency_keywords:
                    if f in cleaned.lower():
                        fluency = f.title()
                        lang_name = re.sub(r'\(?' + f + r'\)?', '', cleaned, flags=re.IGNORECASE).strip("-() ")
                        break
                
                # Basic check to avoid extracting random words
                # Spoken languages are usually single words (e.g. English, French, Mandarin, Hindi)
                if re.match(r'^[A-Z][a-zA-Z]+$', lang_name):
                    entry = {
                        "name": self._create_field(lang_name, 0.9, line),
                        "confidence": 0.9
                    }
                    if fluency:
                        entry["fluency"] = self._create_field(fluency, 0.9, line)
                    parsed.append(entry)
                    
        return parsed

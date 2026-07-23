import re
from typing import List, Dict, Any

class CertificationExtractor:
    def _create_field(self, value: Any, conf: float, source_line: Dict, section: str = "certifications") -> Dict:
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
            
            if blk:
                entry["name"] = self._create_field(blk[0]["text"].lstrip("-•* "), 0.8, blk[0])
            
            for line in blk:
                text = line["text"]
                
                # AWS, Google, Microsoft, Coursera, Udemy etc.
                issuer_match = re.search(r'\b(AWS|Google|Microsoft|Coursera|Udemy|Oracle|Cisco|IBM|CompTIA)\b', text, re.IGNORECASE)
                if issuer_match and "issuer" not in entry:
                    entry["issuer"] = self._create_field(issuer_match.group(1), 0.9, line)
                    
                year_match = re.search(r'\b(20\d{2})\b', text)
                if year_match and "date" not in entry:
                    entry["date"] = self._create_field(year_match.group(1), 0.9, line)
            
            desc_text = "\n".join([l["text"] for l in blk])
            entry["description"] = self._create_field(desc_text, 0.9, blk[0])
            parsed.append(entry)
            
        return parsed

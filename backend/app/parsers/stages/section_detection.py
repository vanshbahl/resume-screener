import re
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import ResumeDocument, PipelineContext

class SectionDetectionStage(BaseParserStage):
    def run(self, document: ResumeDocument, context: PipelineContext) -> None:
        section_patterns = context.config.get("sections", {})
        
        sections = {"personal_info": {"lines": [], "confidence": 1.0}} 
        current_section = "personal_info"
        
        for line_obj in document.cleaned_lines:
            text = line_obj["text"].lower()
            text = re.sub(r':$', '', text)
            
            matched_section = None
            
            # Heuristic: Section headers are usually short lines.
            if len(text) < 40:
                for sec_name, pattern in section_patterns.items():
                    if re.match(pattern, text):
                        matched_section = sec_name
                        break
                        
            if matched_section:
                current_section = matched_section
                if current_section not in sections:
                    sections[current_section] = {"lines": [], "confidence": 0.95}
            else:
                sections[current_section]["lines"].append(line_obj)
                
        document.sections = sections

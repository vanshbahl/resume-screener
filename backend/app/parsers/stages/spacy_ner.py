import time
from typing import Dict, Any
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import BaseDocument, PipelineContext
from app.parsers.ml.model_manager import model_manager

class SpacyNERStage(BaseParserStage):
    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        start_time = time.time()
        
        nlp = model_manager.get_spacy()
        if not nlp:
            context.log_warning("SpacyLoadError", "Spacy model not loaded, skipping stage.")
            return

        text = "\n".join([line["text"] for line in document.raw_lines])
        
        line_starts = []
        curr_idx = 0
        for line in document.raw_lines:
            line_starts.append((curr_idx, line))
            curr_idx += len(line["text"]) + 1
            
        def get_line_obj(char_idx):
            for start, line in reversed(line_starts):
                if char_idx >= start:
                    return line
            return line_starts[0][1] if line_starts else {"page": 1, "line_no": 1}

        doc = nlp(text)
        
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],
            "DATE": [],
            "WORK_OF_ART": []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                line_obj = get_line_obj(ent.start_char)
                entities[ent.label_].append({
                    "value": ent.text,
                    "confidence": 0.9, # Spacy doesn't expose confidence trivially, assume high for Trf
                    "source": {
                        "page": line_obj.get("page", 1),
                        "section": "unknown", # Will be resolved in fusion
                        "line": line_obj.get("line_no", 1)
                    },
                    "origin_model": "spacy"
                })
                
        document.spacy_entities = entities
        
        # Track inference time
        duration = int((time.time() - start_time) * 1000)
        document.metadata["ai_inference_time_ms"] = document.metadata.get("ai_inference_time_ms", 0) + duration
        if "model_versions" not in document.metadata:
            document.metadata["model_versions"] = {}
        document.metadata["model_versions"]["spacy"] = getattr(nlp, "name", "en_core_web_trf")

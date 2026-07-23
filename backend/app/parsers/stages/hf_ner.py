import time
from typing import Dict, Any
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import BaseDocument, PipelineContext
from app.parsers.ml.model_manager import model_manager

class HuggingFaceNERStage(BaseParserStage):
    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        start_time = time.time()
        
        hf_pipeline = model_manager.get_hf_ner()
        if not hf_pipeline:
            context.log_warning("HFLoadError", "HF pipeline not loaded, skipping stage.")
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

        # Truncate text if it's too long for BERT (512 tokens max)
        # 1 token is roughly 4 chars, so limit to 2000 chars to be safe.
        # For full documents, we could chunk it, but for a resume, truncation or chunking is needed.
        # Let's chunk the text by section or just simple windowing to be safe.
        # Simple windowing by chunk of 1500 chars with 200 char overlap
        chunks = []
        window = 1500
        stride = 1300
        for i in range(0, len(text), stride):
            chunks.append((i, text[i:i+window]))
            
        entities = {
            "PER": [],
            "ORG": [],
            "LOC": [],
            "MISC": []
        }
        
        seen_entities = set()

        for offset, chunk in chunks:
            hf_results = hf_pipeline(chunk)
            for res in hf_results:
                label = res.get("entity_group") or res.get("entity") # some pipelines return entity_group for simple aggregation
                word = res.get("word", "").strip()
                score = res.get("score", 0.0)
                start_char = res.get("start", 0) + offset
                
                # Filter out partial subwords or too short words
                if not word or word.startswith("##") or len(word) < 2:
                    continue
                
                # deduplicate
                key = f"{label}-{word}"
                if key not in seen_entities:
                    seen_entities.add(key)
                    
                    if label in entities:
                        line_obj = get_line_obj(start_char)
                        entities[label].append({
                            "value": word,
                            "confidence": round(float(score), 2),
                            "source": {
                                "page": line_obj.get("page", 1),
                                "section": "unknown",
                                "line": line_obj.get("line_no", 1)
                            },
                            "origin_model": "huggingface"
                        })
                
        document.hf_entities = entities
        
        duration = int((time.time() - start_time) * 1000)
        document.metadata["ai_inference_time_ms"] = document.metadata.get("ai_inference_time_ms", 0) + duration
        if "model_versions" not in document.metadata:
            document.metadata["model_versions"] = {}
        document.metadata["model_versions"]["hf_ner"] = getattr(hf_pipeline, "name", "dslim/bert-base-NER")

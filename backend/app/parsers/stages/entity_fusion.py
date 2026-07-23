import time
from typing import Dict, List, Any
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import BaseDocument, JobDocument, PipelineContext

class EntityFusionStage(BaseParserStage):
    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        if isinstance(document, JobDocument):
            self._fuse_jd(document, context)
        else:
            self._fuse_resume(document, context)
            
    def _fuse_jd(self, document: JobDocument, context: PipelineContext) -> None:
        start_time = time.time()
        extracted = document.extracted_entities
        spacy_ents = document.spacy_entities
        hf_ents = document.hf_entities
        
        entities_added = 0
        entities_modified = 0
        
        # JD Company extraction using AI (if missing)
        jm = extracted.get("job_metadata", {})
        if not jm.get("company"):
            best_org = None
            best_conf = 0.0
            best_source = "spacy"
            
            # Usually company name is mentioned early in the JD
            for ent in spacy_ents.get("ORG", []):
                if ent["source"]["line"] <= 10 and ent["confidence"] > best_conf:
                    best_org = ent
                    best_conf = ent["confidence"]
                    best_source = "spacy"
                    
            for ent in hf_ents.get("ORG", []):
                if ent["source"]["line"] <= 10 and ent["confidence"] > best_conf:
                    best_org = ent
                    best_conf = ent["confidence"]
                    best_source = "huggingface"
                    
            if best_org:
                jm["company"] = {
                    "value": best_org["value"],
                    "confidence": best_org["confidence"],
                    "source": best_org["source"],
                    "origin_model": best_source
                }
                entities_added += 1
                
        extracted["job_metadata"] = jm
        document.normalized_entities = extracted
        
        document.metadata["entities_added_by_ai"] = document.metadata.get("entities_added_by_ai", 0) + entities_added
        document.metadata["entities_modified_by_ai"] = document.metadata.get("entities_modified_by_ai", 0) + entities_modified

    def _fuse_resume(self, document: BaseDocument, context: PipelineContext) -> None:
        start_time = time.time()
        
        extracted = document.extracted_entities
        spacy_ents = document.spacy_entities
        hf_ents = document.hf_entities
        
        entities_added = 0
        entities_modified = 0
        
        # 1. Personal Info Merging
        pi = extracted.get("personal_info", {})
        
        # AI Name detection (if missing or if we want to cross-verify)
        # HF uses "PER" or "I-PER"
        if not pi.get("name") or not pi["name"].get("value"):
            # Try to find a PERSON in the first few lines using HF or Spacy
            best_ai_name = None
            best_conf = 0.0
            best_source = "spacy"
            
            for ent in spacy_ents.get("PERSON", []):
                if ent["source"]["line"] <= 5 and ent["confidence"] > best_conf:
                    best_ai_name = ent
                    best_conf = ent["confidence"]
                    best_source = "spacy"
                    
            for ent in hf_ents.get("PER", []):
                if ent["source"]["line"] <= 5 and ent["confidence"] > best_conf:
                    best_ai_name = ent
                    best_conf = ent["confidence"]
                    best_source = "huggingface"
                    
            if best_ai_name:
                pi["name"] = {
                    "value": best_ai_name["value"],
                    "confidence": best_ai_name["confidence"],
                    "source": best_ai_name["source"],
                    "origin_model": best_source
                }
                entities_added += 1

        # 2. Experience ORG extraction
        # If deterministic missed company name, or if AI gives a better one
        for exp in extracted.get("experience", []):
            if not exp.get("company"):
                # find an ORG in the same lines as this experience block
                start_line = exp["description"]["source"]["line"] if exp.get("description") else 1
                end_line = start_line + 5 # approximate search window
                
                best_org = None
                best_conf = 0.0
                best_source = "spacy"
                
                for ent in spacy_ents.get("ORG", []):
                    if start_line <= ent["source"]["line"] <= end_line and ent["confidence"] > best_conf:
                        best_org = ent
                        best_conf = ent["confidence"]
                        best_source = "spacy"
                        
                for ent in hf_ents.get("ORG", []):
                    if start_line <= ent["source"]["line"] <= end_line and ent["confidence"] > best_conf:
                        best_org = ent
                        best_conf = ent["confidence"]
                        best_source = "huggingface"
                        
                if best_org:
                    exp["company"] = {
                        "value": best_org["value"],
                        "confidence": best_org["confidence"],
                        "source": best_org["source"],
                        "origin_model": best_source
                    }
                    entities_added += 1
            else:
                # If deterministic got a company, check if HF/Spacy got a better/longer name
                # e.g., deterministic = "Tech", AI = "Tech Innovations Inc."
                det_comp = exp["company"]["value"]
                
                start_line = exp["company"]["source"]["line"] if exp.get("company") and exp["company"].get("source") else 1
                
                for ent in hf_ents.get("ORG", []) + spacy_ents.get("ORG", []):
                    if ent["source"]["line"] == start_line and ent["confidence"] > 0.85:
                        if det_comp in ent["value"] and len(ent["value"]) > len(det_comp):
                            exp["company"]["value"] = ent["value"]
                            exp["company"]["origin_model"] = "fusion"
                            entities_modified += 1
                            break

        # 3. Location extraction for Experience
        for exp in extracted.get("experience", []):
            if not exp.get("location"):
                start_line = exp["description"]["source"]["line"] if exp.get("description") else 1
                end_line = start_line + 5
                
                best_loc = None
                best_conf = 0.0
                best_source = "spacy"
                
                # Check GPE (Geopolitical Entity) in Spacy
                for ent in spacy_ents.get("GPE", []):
                    if start_line <= ent["source"]["line"] <= end_line and ent["confidence"] > best_conf:
                        best_loc = ent
                        best_conf = ent["confidence"]
                        best_source = "spacy"
                        
                # Check LOC in HF
                for ent in hf_ents.get("LOC", []):
                    if start_line <= ent["source"]["line"] <= end_line and ent["confidence"] > best_conf:
                        best_loc = ent
                        best_conf = ent["confidence"]
                        best_source = "huggingface"
                        
                if best_loc:
                    exp["location"] = {
                        "value": best_loc["value"],
                        "confidence": best_loc["confidence"],
                        "source": best_loc["source"],
                        "origin_model": best_source
                    }
                    entities_added += 1

        # We will write the fused state into normalized_entities for the next stage
        document.normalized_entities = extracted
        
        duration = int((time.time() - start_time) * 1000)
        
        # Record stats
        if "metadata" not in document.final_json:
            pass # Will be handled by validation stage, we should store in document.metadata
            
        document.metadata["entities_added_by_ai"] = document.metadata.get("entities_added_by_ai", 0) + entities_added
        document.metadata["entities_modified_by_ai"] = document.metadata.get("entities_modified_by_ai", 0) + entities_modified

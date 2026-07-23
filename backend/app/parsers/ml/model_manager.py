import logging

import spacy
import torch
from transformers import pipeline

logger = logging.getLogger(__name__)


class ModelManager:
    _instance = None
    _spacy_model = None
    _hf_pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def get_spacy(self):
        if self._spacy_model is None:
            try:
                logger.info("Loading spacy model 'en_core_web_trf'...")
                self._spacy_model = spacy.load("en_core_web_trf")
                self._spacy_model.name = "en_core_web_trf"
            except Exception as e:
                logger.warning(
                    f"Failed to load en_core_web_trf, falling back to en_core_web_md. Error: {e}"
                )
                self._spacy_model = spacy.load("en_core_web_md")
                self._spacy_model.name = "en_core_web_md"
        return self._spacy_model

    def get_hf_ner(self):
        if self._hf_pipeline is None:
            model_name = "dslim/bert-base-NER"
            logger.info(f"Loading HuggingFace NER model '{model_name}'...")
            device = (
                "cuda"
                if torch.cuda.is_available()
                else ("mps" if torch.backends.mps.is_available() else "cpu")
            )
            # Create NER pipeline
            # aggregation_strategy="simple" merges B- and I- tokens into one entity
            self._hf_pipeline = pipeline(
                "ner", model=model_name, aggregation_strategy="simple", device=device
            )
            self._hf_pipeline.name = model_name
        return self._hf_pipeline


# Global instance for easy access
model_manager = ModelManager()

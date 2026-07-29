"""Tests for parser feature flags.

Verifies that the pipeline builder conditionally includes/excludes stages
based on the feature flag configuration. No real model loading required.
"""

from unittest.mock import patch

import pytest

from app.candidate.services.resume_service import get_default_pipeline
from app.parsers.stages.hf_ner import HuggingFaceNERStage
from app.parsers.stages.spacy_ner import SpacyNERStage
from app.parsers.stages.entity_fusion import EntityFusionStage


def _build_pipeline_with_flags(**flag_overrides) -> object:
    """Build a pipeline with specific feature flag overrides."""
    flags = {
        "spacy_ner": True,
        "hf_ner": True,
        "entity_fusion": True,
        "completeness": True,
        "health_report": True,
        "ocr_fallback": True,
        **flag_overrides,
    }
    config = {"parser": {"feature_flags": flags}}
    with patch("app.candidate.services.resume_service.load_config", return_value=config):
        return get_default_pipeline()


def _stage_types(pipeline) -> list:
    return [type(s) for s in pipeline.stages]


class TestFeatureFlags:
    def test_all_flags_enabled_includes_all_stages(self):
        pipeline = _build_pipeline_with_flags()
        types = _stage_types(pipeline)
        assert SpacyNERStage in types
        assert HuggingFaceNERStage in types
        assert EntityFusionStage in types

    def test_spacy_flag_disabled_excludes_spacy_stage(self):
        pipeline = _build_pipeline_with_flags(spacy_ner=False)
        types = _stage_types(pipeline)
        assert SpacyNERStage not in types

    def test_hf_ner_flag_disabled_excludes_hf_stage(self):
        pipeline = _build_pipeline_with_flags(hf_ner=False)
        types = _stage_types(pipeline)
        assert HuggingFaceNERStage not in types

    def test_entity_fusion_flag_disabled_excludes_fusion(self):
        pipeline = _build_pipeline_with_flags(entity_fusion=False)
        types = _stage_types(pipeline)
        assert EntityFusionStage not in types

    def test_all_ner_disabled_excludes_both(self):
        pipeline = _build_pipeline_with_flags(spacy_ner=False, hf_ner=False)
        types = _stage_types(pipeline)
        assert SpacyNERStage not in types
        assert HuggingFaceNERStage not in types

    def test_active_flags_recorded_on_pipeline(self):
        pipeline = _build_pipeline_with_flags(spacy_ner=True, hf_ner=False)
        assert hasattr(pipeline, "active_flags")
        assert "spacy_ner" in pipeline.active_flags
        assert "hf_ner" not in pipeline.active_flags

import time
from typing import List, Dict, Any
from dataclasses import dataclass, field
from app.parsers.core.exceptions import ParserWarning
from app.parsers.core.config_loader import get_parser_config

@dataclass
class PipelineContext:
    current_stage: str = "init"
    execution_timestamps: Dict[str, float] = field(default_factory=dict)
    warnings: List[ParserWarning] = field(default_factory=list)
    recoverable_errors: List[str] = field(default_factory=list)
    parser_statistics: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=get_parser_config)

    def log_warning(self, w_type: str, message: str, line_no: int = None):
        self.warnings.append(ParserWarning(type=w_type, message=message, stage=self.current_stage, line_no=line_no))

    def log_error(self, message: str):
        self.recoverable_errors.append(f"[{self.current_stage}] {message}")

    def record_stage_time(self, stage_name: str, duration_ms: float):
        self.execution_timestamps[stage_name] = duration_ms

class ResumeDocument:
    def __init__(self, file_path: str, resume_id: int = None, job_id: int = None):
        self.file_path = file_path
        self.resume_id = resume_id
        self.job_id = job_id
        
        self.metadata: Dict[str, Any] = {}
        self.raw_lines: List[Dict[str, Any]] = []
        self.cleaned_lines: List[Dict[str, Any]] = []
        self.sections: Dict[str, dict] = {}
        self.extracted_entities: Dict[str, Any] = {}
        self.spacy_entities: Dict[str, Any] = {}
        self.hf_entities: Dict[str, Any] = {}
        self.fusion_entities: Dict[str, Any] = {}
        self.normalized_entities: Dict[str, Any] = {}
        self.validation_results: bool = False
        self.final_json: Dict[str, Any] = {}

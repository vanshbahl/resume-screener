import time
from typing import List
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import ResumeDocument, PipelineContext
from app.parsers.core.exceptions import ParserFatalError

class ParserPipeline:
    def __init__(self, stages: List[BaseParserStage]):
        self.stages = stages
        
    def run(self, document: ResumeDocument) -> ResumeDocument:
        context = PipelineContext()
        pipeline_start = time.time()
        
        for stage in self.stages:
            context.current_stage = stage.name
            stage_start = time.time()
            try:
                stage.run(document, context)
            except ParserFatalError as e:
                context.log_error(f"Fatal error in {stage.name}: {e}")
                raise
            except Exception as e:
                context.log_error(f"Recoverable error in {stage.name}: {e}")
            finally:
                duration = (time.time() - stage_start) * 1000
                context.record_stage_time(stage.name, duration)
                
        pipeline_duration = (time.time() - pipeline_start) * 1000
        
        if document.final_json and "metadata" in document.final_json:
            document.final_json["metadata"]["processing_time_ms"] = int(pipeline_duration)
            document.final_json["metadata"]["warnings"] = [
                {"type": w.type, "message": w.message, "stage": w.stage, "line": w.line_no}
                for w in context.warnings
            ]
            document.final_json["metadata"]["recoverable_errors"] = context.recoverable_errors
            document.final_json["metadata"]["execution_timestamps"] = context.execution_timestamps
            
        return document

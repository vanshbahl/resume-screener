from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import ResumeDocument, PipelineContext

class NormalizationStage(BaseParserStage):
    def run(self, document: ResumeDocument, context: PipelineContext) -> None:
        document.normalized_entities = document.extracted_entities

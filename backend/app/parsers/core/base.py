from abc import ABC, abstractmethod
from app.parsers.core.document import ResumeDocument, PipelineContext

class BaseParserStage(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def run(self, document: ResumeDocument, context: PipelineContext) -> None:
        pass

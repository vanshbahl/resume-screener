from abc import ABC, abstractmethod
from app.parsers.core.document import BaseDocument, PipelineContext

class BaseParserStage(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        pass

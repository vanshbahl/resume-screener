from abc import ABC, abstractmethod
from typing import Set
from app.schemas.search import SearchContext
from app.search.index.manager import index_manager

class SearchStrategy(ABC):
    """Base interface for all search execution strategies."""
    
    def __init__(self):
        self.index_manager = index_manager
    
    @abstractmethod
    def execute(self, context: SearchContext) -> Set[str]:
        """
        Executes the search and returns a set of matching target IDs.
        Un-ranked. Ranking happens later in the pipeline.
        """
        pass

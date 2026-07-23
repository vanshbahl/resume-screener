from typing import List, Optional
from sqlalchemy.orm import Session
from app.workspace.repositories.workspace import WorkspaceRepository
from app.workspace.schemas.workspace import SavedSearchCreate, SavedSearchUpdate, SavedSearchResponse

class SavedSearchService:
    def __init__(self, db: Session):
        self.repo = WorkspaceRepository(db)

    def get_saved_searches(self, user_id: str) -> List[SavedSearchResponse]:
        searches = self.repo.get_saved_searches(user_id)
        return [SavedSearchResponse.model_validate(s) for s in searches]

    def create_search(self, user_id: str, search: SavedSearchCreate) -> SavedSearchResponse:
        s = self.repo.create_saved_search(user_id, search)
        return SavedSearchResponse.model_validate(s)

    def update_search(self, search_id: str, search: SavedSearchUpdate) -> Optional[SavedSearchResponse]:
        s = self.repo.update_saved_search(search_id, search)
        if s:
            return SavedSearchResponse.model_validate(s)
        return None

    def delete_search(self, search_id: str) -> bool:
        return self.repo.delete_saved_search(search_id)

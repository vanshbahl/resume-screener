from typing import List, Optional
from sqlalchemy.orm import Session
from app.workspace.repositories.workspace import WorkspaceRepository
from app.workspace.schemas.workspace import FavoriteCreate, FavoriteResponse

class FavoriteService:
    def __init__(self, db: Session):
        self.repo = WorkspaceRepository(db)

    def get_favorites(self, user_id: str, entity_type: Optional[str] = None) -> List[FavoriteResponse]:
        favs = self.repo.get_favorites(user_id, entity_type=entity_type)
        return [FavoriteResponse.model_validate(f) for f in favs]

    def add_favorite(self, user_id: str, favorite: FavoriteCreate) -> FavoriteResponse:
        f = self.repo.add_favorite(user_id, favorite)
        return FavoriteResponse.model_validate(f)

    def remove_favorite(self, user_id: str, entity_type: str, entity_id: str) -> bool:
        return self.repo.remove_favorite(user_id, entity_type, entity_id)

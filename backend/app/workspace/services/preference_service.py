from sqlalchemy.orm import Session
from app.workspace.repositories.workspace import WorkspaceRepository
from app.workspace.schemas.workspace import PreferenceUpdate, PreferenceResponse

class PreferenceService:
    def __init__(self, db: Session):
        self.repo = WorkspaceRepository(db)

    def get_preferences(self, user_id: str) -> PreferenceResponse:
        p = self.repo.get_preferences(user_id)
        return PreferenceResponse.model_validate(p)

    def update_preferences(self, user_id: str, prefs: PreferenceUpdate) -> PreferenceResponse:
        p = self.repo.update_preferences(user_id, prefs)
        return PreferenceResponse.model_validate(p)

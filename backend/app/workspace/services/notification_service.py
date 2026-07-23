from typing import List
from sqlalchemy.orm import Session
from app.workspace.repositories.workspace import WorkspaceRepository
from app.workspace.schemas.workspace import NotificationCreate, NotificationResponse

class NotificationService:
    def __init__(self, db: Session):
        self.repo = WorkspaceRepository(db)

    def get_notifications(self, user_id: str, unread_only: bool = False) -> List[NotificationResponse]:
        notifs = self.repo.get_notifications(user_id, unread_only=unread_only)
        return [NotificationResponse.model_validate(n) for n in notifs]

    def create_notification(self, notification: NotificationCreate) -> NotificationResponse:
        n = self.repo.create_notification(notification)
        return NotificationResponse.model_validate(n)

    def mark_as_read(self, notification_id: str) -> bool:
        return self.repo.mark_notification_read(notification_id)

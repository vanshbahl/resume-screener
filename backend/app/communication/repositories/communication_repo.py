from typing import List, Optional
from sqlalchemy.orm import Session
from app.communication.models.communication import (
    NotificationTemplate, CommunicationNotification, CommunicationPreference, 
    DeliveryAttempt, NotificationQueue, CommunicationAudit
)
from app.workspace.caching.memory import memory_cache # reusing cache for preferences/templates

class CommunicationRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Templates ---
    def get_template(self, template_id: int) -> Optional[NotificationTemplate]:
        return self.db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
        
    def get_template_by_name(self, name: str) -> Optional[NotificationTemplate]:
        return self.db.query(NotificationTemplate).filter(NotificationTemplate.name == name, NotificationTemplate.is_active == True).first()

    def create_template(self, template: NotificationTemplate) -> NotificationTemplate:
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    # --- Notifications ---
    def create_notification(self, notification: CommunicationNotification) -> CommunicationNotification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_notification(self, notification_id: int) -> Optional[CommunicationNotification]:
        return self.db.query(CommunicationNotification).filter(CommunicationNotification.id == notification_id).first()

    def update_notification(self, notification: CommunicationNotification):
        self.db.commit()
        self.db.refresh(notification)

    # --- Preferences ---
    def get_preference(self, user_id: int) -> Optional[CommunicationPreference]:
        # Using simple caching for preferences
        cache_key = f"comm_pref_{user_id}"
        cached = memory_cache.get(cache_key)
        if cached:
            return cached
            
        pref = self.db.query(CommunicationPreference).filter(CommunicationPreference.user_id == user_id).first()
        if pref:
            memory_cache.set(cache_key, pref, ttl_seconds=300)
        return pref
        
    def set_preference(self, pref: CommunicationPreference) -> CommunicationPreference:
        existing = self.db.query(CommunicationPreference).filter(CommunicationPreference.user_id == pref.user_id).first()
        if existing:
            existing.enable_email = pref.enable_email
            existing.enable_sms = pref.enable_sms
            existing.enable_push = pref.enable_push
            existing.enable_in_app = pref.enable_in_app
            existing.quiet_hours_start = pref.quiet_hours_start
            existing.quiet_hours_end = pref.quiet_hours_end
            existing.timezone = pref.timezone
            existing.language = pref.language
            pref = existing
        else:
            self.db.add(pref)
        
        self.db.commit()
        self.db.refresh(pref)
        memory_cache.delete(f"comm_pref_{pref.user_id}")
        return pref

    # --- Delivery Attempts ---
    def create_delivery_attempt(self, attempt: DeliveryAttempt) -> DeliveryAttempt:
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    # --- Queue ---
    def add_to_queue(self, queue_item: NotificationQueue) -> NotificationQueue:
        self.db.add(queue_item)
        self.db.commit()
        self.db.refresh(queue_item)
        return queue_item
        
    def get_pending_queue_items(self, limit: int = 100) -> List[NotificationQueue]:
        from app.communication.models.communication import QueueStatus
        return self.db.query(NotificationQueue).filter(NotificationQueue.status == QueueStatus.PENDING).order_by(NotificationQueue.priority.desc(), NotificationQueue.created_at.asc()).limit(limit).all()

    def update_queue_item(self, queue_item: NotificationQueue):
        self.db.commit()
        self.db.refresh(queue_item)

    # --- Audit ---
    def log_audit(self, audit: CommunicationAudit):
        self.db.add(audit)
        self.db.commit()

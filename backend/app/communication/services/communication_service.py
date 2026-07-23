from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.communication.models.communication import (
    CommunicationNotification, NotificationStatus, QueueStatus, NotificationQueue,
    DeliveryAttempt, TemplateVersion, CommunicationPreference
)
from app.communication.repositories.communication_repo import CommunicationRepository
from app.communication.templates.engine import template_engine
from app.communication.providers.mock import (
    MockEmailProvider, MockSMSProvider, MockPushProvider, MockWebhookProvider
)

class TemplateService:
    def __init__(self, repo: CommunicationRepository):
        self.repo = repo

    def render_template(self, template_name: str, payload: Dict[str, Any]) -> str:
        template = self.repo.get_template_by_name(template_name)
        if not template or not template.versions:
            raise ValueError(f"Template {template_name} not found or has no versions")
            
        # Get latest published version
        published_versions = [v for v in template.versions if v.is_published]
        if not published_versions:
            version = template.versions[-1] # fallback to latest
        else:
            version = sorted(published_versions, key=lambda x: x.version)[-1]
            
        return template_engine.render(version.body_template, payload)

class PreferenceService:
    def __init__(self, repo: CommunicationRepository):
        self.repo = repo

    def get_user_preferences(self, user_id: int) -> CommunicationPreference:
        pref = self.repo.get_preference(user_id)
        if not pref:
            # Return defaults if none set
            pref = CommunicationPreference(user_id=user_id)
            self.repo.set_preference(pref)
        return pref
        
    def should_deliver(self, pref: CommunicationPreference, channel: str) -> bool:
        if channel == "EMAIL": return pref.enable_email
        if channel == "SMS": return pref.enable_sms
        if channel == "PUSH": return pref.enable_push
        if channel == "IN_APP": return pref.enable_in_app
        return True # Webhooks etc

class DeliveryService:
    def __init__(self, repo: CommunicationRepository):
        self.repo = repo
        self.email_provider = MockEmailProvider()
        self.sms_provider = MockSMSProvider()
        self.push_provider = MockPushProvider()
        self.webhook_provider = MockWebhookProvider()
        self.template_svc = TemplateService(repo)

    def process_notification(self, notification_id: int) -> bool:
        notification = self.repo.get_notification(notification_id)
        if not notification:
            return False
            
        if notification.status != NotificationStatus.QUEUED:
            return False
            
        notification.status = NotificationStatus.PROCESSING
        self.repo.update_notification(notification)
        
        # Determine actual content
        try:
            if notification.template_id:
                template = self.repo.get_template(notification.template_id)
                body = self.template_svc.render_template(template.name, notification.payload or {})
                subject = f"Notification: {notification.event_type}"
            else:
                body = str(notification.payload)
                subject = f"Alert: {notification.event_type}"
        except Exception as e:
            # Template rendering failed
            notification.status = NotificationStatus.FAILED
            self.repo.update_notification(notification)
            self._log_attempt(notification, "SYSTEM", "FAILED", str(e))
            return False

        # Check preferences if user_id present
        if notification.recipient_user_id:
            pref_svc = PreferenceService(self.repo)
            pref = pref_svc.get_user_preferences(notification.recipient_user_id)
            if not pref_svc.should_deliver(pref, notification.channel):
                notification.status = NotificationStatus.CANCELLED
                self.repo.update_notification(notification)
                self._log_attempt(notification, "SYSTEM", "CANCELLED", "User preferences disabled this channel")
                return True # Handled successfully

        # Send via provider
        success = False
        attempt_result = {}
        provider_name = "Unknown"
        error_message = None
        
        try:
            if notification.channel == "EMAIL" and notification.recipient_email:
                provider_name = self.email_provider.provider_name
                attempt_result = self.email_provider.send_email(notification.recipient_email, subject, body)
            elif notification.channel == "SMS" and notification.recipient_phone:
                provider_name = self.sms_provider.provider_name
                attempt_result = self.sms_provider.send_sms(notification.recipient_phone, body)
            elif notification.channel == "PUSH":
                provider_name = self.push_provider.provider_name
                # Mock device token logic
                attempt_result = self.push_provider.send_push("token-123", subject, body)
            elif notification.channel == "WEBHOOK":
                provider_name = self.webhook_provider.provider_name
                endpoint = notification.payload.get("webhook_url", "http://localhost/webhook")
                attempt_result = self.webhook_provider.send_webhook(endpoint, notification.payload)
            else:
                raise ValueError("Invalid channel or missing contact info")
                
            success = attempt_result.get("status") == "SUCCESS"
            
        except Exception as e:
            error_message = str(e)
            
        if success:
            notification.status = NotificationStatus.DELIVERED
            self.repo.update_notification(notification)
            self._log_attempt(notification, provider_name, "SUCCESS", None, attempt_result.get("provider_message_id"))
            return True
        else:
            notification.status = NotificationStatus.FAILED
            self.repo.update_notification(notification)
            self._log_attempt(notification, provider_name, "FAILED", error_message or attempt_result.get("error"))
            return False
            
    def _log_attempt(self, notification: CommunicationNotification, provider: str, status: str, error: str = None, msg_id: str = None):
        attempt = DeliveryAttempt(
            notification_id=notification.id,
            provider=provider,
            status=status,
            error_message=error,
            provider_message_id=msg_id
        )
        self.repo.create_delivery_attempt(attempt)

class CommunicationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CommunicationRepository(db)
        self.template_svc = TemplateService(self.repo)
        self.pref_svc = PreferenceService(self.repo)
        self.delivery_svc = DeliveryService(self.repo)

    def publish_event(self, event_type: str, payload: Dict[str, Any], user_id: Optional[int] = None, email: Optional[str] = None, phone: Optional[str] = None, force_channel: Optional[str] = None) -> CommunicationNotification:
        """
        The main entrypoint for domains to publish communication events.
        """
        # Determine channel. In real system, might lookup template default
        channel = force_channel or "EMAIL"
        
        notification = CommunicationNotification(
            event_type=event_type,
            recipient_user_id=user_id,
            recipient_email=email,
            recipient_phone=phone,
            channel=channel,
            payload=payload,
            status=NotificationStatus.QUEUED
        )
        self.repo.create_notification(notification)
        
        # Add to queue
        queue_item = NotificationQueue(
            notification_id=notification.id,
            status=QueueStatus.PENDING,
            priority=10
        )
        self.repo.add_to_queue(queue_item)
        return notification

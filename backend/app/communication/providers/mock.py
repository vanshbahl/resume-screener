from typing import Dict, Any, Optional
import uuid
import logging
from .base import BaseEmailProvider, BaseSMSProvider, BasePushProvider, BaseWebhookProvider

logger = logging.getLogger(__name__)

class MockEmailProvider(BaseEmailProvider):
    @property
    def provider_name(self) -> str:
        return "MockEmail"

    def send_email(self, to_address: str, subject: str, html_body: str, text_body: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"[MockEmail] Sending to {to_address} | Subject: {subject}")
        # Always succeed
        return {
            "status": "SUCCESS",
            "provider_message_id": f"mock-email-{uuid.uuid4()}"
        }

class MockSMSProvider(BaseSMSProvider):
    @property
    def provider_name(self) -> str:
        return "MockSMS"

    def send_sms(self, to_phone: str, body: str) -> Dict[str, Any]:
        logger.info(f"[MockSMS] Sending to {to_phone} | Body: {body}")
        return {
            "status": "SUCCESS",
            "provider_message_id": f"mock-sms-{uuid.uuid4()}"
        }

class MockPushProvider(BasePushProvider):
    @property
    def provider_name(self) -> str:
        return "MockPush"

    def send_push(self, device_token: str, title: str, body: str) -> Dict[str, Any]:
        logger.info(f"[MockPush] Sending to {device_token} | Title: {title}")
        return {
            "status": "SUCCESS",
            "provider_message_id": f"mock-push-{uuid.uuid4()}"
        }

class MockWebhookProvider(BaseWebhookProvider):
    @property
    def provider_name(self) -> str:
        return "MockWebhook"

    def send_webhook(self, endpoint_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[MockWebhook] Sending to {endpoint_url} | Payload keys: {list(payload.keys())}")
        return {
            "status": "SUCCESS",
            "provider_message_id": f"mock-webhook-{uuid.uuid4()}"
        }

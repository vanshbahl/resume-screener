from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

class BaseEmailProvider(BaseProvider):
    @abstractmethod
    def send_email(self, to_address: str, subject: str, html_body: str, text_body: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an email and return a dict with status and provider_message_id.
        """
        pass

class BaseSMSProvider(BaseProvider):
    @abstractmethod
    def send_sms(self, to_phone: str, body: str) -> Dict[str, Any]:
        pass

class BasePushProvider(BaseProvider):
    @abstractmethod
    def send_push(self, device_token: str, title: str, body: str) -> Dict[str, Any]:
        pass

class BaseWebhookProvider(BaseProvider):
    @abstractmethod
    def send_webhook(self, endpoint_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

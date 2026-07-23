from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TemplateVersionBase(BaseModel):
    version: int
    subject_template: Optional[str] = None
    body_template: str
    is_published: bool = False

class TemplateVersionResponse(TemplateVersionBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NotificationTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    channel: str
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    initial_version: TemplateVersionBase

class NotificationTemplateResponse(NotificationTemplateBase):
    id: int
    organization_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    versions: List[TemplateVersionResponse] = []
    model_config = ConfigDict(from_attributes=True)

class NotificationPublishEvent(BaseModel):
    event_type: str
    recipient_user_id: Optional[int] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    channel: Optional[str] = None # Force a specific channel, or let preferences decide
    payload: Dict[str, Any]

class NotificationResponse(BaseModel):
    id: int
    organization_id: Optional[int]
    event_type: str
    recipient_user_id: Optional[int]
    recipient_email: Optional[str]
    recipient_phone: Optional[str]
    channel: str
    status: str
    template_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CommunicationPreferenceBase(BaseModel):
    enable_email: bool = True
    enable_sms: bool = False
    enable_push: bool = True
    enable_in_app: bool = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"

class CommunicationPreferenceResponse(CommunicationPreferenceBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

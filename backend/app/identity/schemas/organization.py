from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class OrganizationSettingsBase(BaseModel):
    branding: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    subscription: Dict[str, Any] = Field(default_factory=dict)

class OrganizationSettingsCreate(OrganizationSettingsBase):
    pass

class OrganizationSettingsResponse(OrganizationSettingsBase):
    id: int
    organization_id: int

    model_config = ConfigDict(from_attributes=True)

class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=255)

class OrganizationCreate(OrganizationBase):
    slug: str = Field(..., max_length=255)

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    settings: Optional[OrganizationSettingsBase] = None

class OrganizationResponse(OrganizationBase):
    id: int
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    settings: Optional[OrganizationSettingsResponse] = None

    model_config = ConfigDict(from_attributes=True)

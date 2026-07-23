from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class RefreshRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class SessionResponse(BaseModel):
    id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device: Optional[str] = None
    is_revoked: bool
    expires_at: datetime
    last_activity: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ApiKeyCreate(BaseModel):
    name: str = Field(..., max_length=100)
    scopes: Dict[str, Any] = Field(default_factory=dict)
    organization_id: int
    expires_in_days: Optional[int] = None

class ApiKeyResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    scopes: Dict[str, Any]
    is_revoked: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ApiKeySecretResponse(ApiKeyResponse):
    api_key: str  # Only returned on creation

class InvitationCreate(BaseModel):
    email: EmailStr
    role_id: int
    organization_id: int

class InvitationResponse(BaseModel):
    id: int
    organization_id: int
    email: str
    role_id: int
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

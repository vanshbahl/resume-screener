from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class PermissionBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_system_role: bool = False

class RoleCreate(RoleBase):
    organization_id: int
    permissions: List[int] = Field(default_factory=list)

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[int]] = None

class RoleResponse(RoleBase):
    id: int
    organization_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoleWithPermissionsResponse(RoleResponse):
    permissions: List[PermissionResponse] = Field(default_factory=list)

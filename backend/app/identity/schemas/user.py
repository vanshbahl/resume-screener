from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    organization_id: int

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    organization_id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    organization_id: int

class DepartmentResponse(DepartmentBase):
    id: int
    organization_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TeamBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    department_id: Optional[int] = None
    parent_id: Optional[int] = None

class TeamCreate(TeamBase):
    organization_id: int

class TeamResponse(TeamBase):
    id: int
    organization_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MembershipBase(BaseModel):
    team_id: Optional[int] = None
    role_id: int

class MembershipCreate(MembershipBase):
    user_id: int

class MembershipResponse(MembershipBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

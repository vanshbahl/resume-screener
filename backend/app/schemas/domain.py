from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from app.models.domain import ResumeStatus

class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: List[str] = []

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ResumeBase(BaseModel):
    filename: str

class ResumeResponse(ResumeBase):
    id: int
    job_id: int
    status: ResumeStatus
    parsed_metadata: Optional[Any] = None
    final_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

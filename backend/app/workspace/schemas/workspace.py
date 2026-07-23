from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# --- Saved Search ---

class SavedSearchBase(BaseModel):
    name: str
    search_type: str = Field(..., description="candidate, job, or workflow")
    criteria: Dict[str, Any]

class SavedSearchCreate(SavedSearchBase):
    pass

class SavedSearchUpdate(BaseModel):
    name: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None

class SavedSearchResponse(SavedSearchBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# --- Favorite ---

class FavoriteBase(BaseModel):
    entity_type: str = Field(..., description="candidate or job")
    entity_id: str
    folder: Optional[str] = None

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    id: int
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

# --- Preference ---

class PreferenceBase(BaseModel):
    settings: Dict[str, Any]

class PreferenceUpdate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: int
    user_id: str
    updated_at: datetime

    model_config = {"from_attributes": True}

# --- Notification ---

class NotificationBase(BaseModel):
    type: str
    content: Dict[str, Any]

class NotificationCreate(NotificationBase):
    user_id: str

class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}

# --- Dashboard & Aggregations ---

class DashboardSummary(BaseModel):
    open_jobs: int
    assigned_candidates: int
    interviews_today: int
    pending_approvals: int
    recent_activity_count: int

class WorkspaceAnalytics(BaseModel):
    candidates_reviewed_today: int
    jobs_managed: int
    interviews_scheduled: int
    offers_generated: int
    tasks_completed: int

class ActivityFeedItem(BaseModel):
    id: str
    domain: str # e.g. "candidate", "job", "workflow"
    event_type: str
    details: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None

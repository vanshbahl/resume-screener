from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.workspace.schemas.workspace import (
    DashboardSummary, 
    ActivityFeedItem, 
    SavedSearchCreate, 
    SavedSearchResponse,
    FavoriteCreate,
    FavoriteResponse,
    PreferenceUpdate,
    PreferenceResponse,
    NotificationResponse,
    WorkspaceAnalytics
)

from app.workspace.services.dashboard_service import DashboardService
from app.workspace.services.work_queue_service import WorkQueueService
from app.workspace.services.activity_feed_service import ActivityFeedService
from app.workspace.services.saved_search_service import SavedSearchService
from app.workspace.services.favorite_service import FavoriteService
from app.workspace.services.preference_service import PreferenceService
from app.workspace.services.notification_service import NotificationService
from app.workspace.services.analytics_service import AnalyticsService
from app.workspace.services.quick_action_service import QuickActionService

router = APIRouter(prefix="/workspace", tags=["Workspace"])

# We simulate a logged-in recruiter for now
FAKE_USER_ID = "recruiter_001"

@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(db: Session = Depends(get_db)):
    svc = DashboardService(db)
    return svc.get_dashboard_summary(FAKE_USER_ID)

@router.get("/activity", response_model=List[ActivityFeedItem])
def get_activity_feed(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    svc = ActivityFeedService(db)
    return svc.get_global_activity_feed(limit=limit, offset=offset)

@router.get("/queue/candidates", response_model=List[dict])
def get_candidate_queue(db: Session = Depends(get_db)):
    svc = WorkQueueService(db)
    return svc.get_candidates_awaiting_review()

@router.get("/queue/jobs", response_model=List[dict])
def get_job_queue(db: Session = Depends(get_db)):
    svc = WorkQueueService(db)
    return svc.get_high_priority_jobs()

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(unread_only: bool = False, db: Session = Depends(get_db)):
    svc = NotificationService(db)
    return svc.get_notifications(FAKE_USER_ID, unread_only=unread_only)

@router.patch("/preferences", response_model=PreferenceResponse)
def update_preferences(prefs: PreferenceUpdate, db: Session = Depends(get_db)):
    svc = PreferenceService(db)
    return svc.update_preferences(FAKE_USER_ID, prefs)

@router.get("/searches", response_model=List[SavedSearchResponse])
def get_searches(db: Session = Depends(get_db)):
    svc = SavedSearchService(db)
    return svc.get_saved_searches(FAKE_USER_ID)

@router.post("/searches", response_model=SavedSearchResponse)
def create_search(search: SavedSearchCreate, db: Session = Depends(get_db)):
    svc = SavedSearchService(db)
    return svc.create_search(FAKE_USER_ID, search)

@router.delete("/searches/{search_id}")
def delete_search(search_id: str, db: Session = Depends(get_db)):
    svc = SavedSearchService(db)
    if not svc.delete_search(search_id):
        raise HTTPException(status_code=404, detail="Saved search not found")
    return {"status": "deleted"}

@router.get("/favorites", response_model=List[FavoriteResponse])
def get_favorites(entity_type: str = None, db: Session = Depends(get_db)):
    svc = FavoriteService(db)
    return svc.get_favorites(FAKE_USER_ID, entity_type=entity_type)

@router.post("/favorites", response_model=FavoriteResponse)
def add_favorite(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    svc = FavoriteService(db)
    return svc.add_favorite(FAKE_USER_ID, favorite)

@router.post("/actions/advance-workflow")
def advance_workflow(pipeline_id: int, to_stage: str, db: Session = Depends(get_db)):
    svc = QuickActionService(db)
    success = svc.advance_workflow(pipeline_id, to_stage, FAKE_USER_ID)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to advance workflow")
    return {"status": "success"}

@router.get("/analytics", response_model=WorkspaceAnalytics)
def get_analytics(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.get_recruiter_analytics(FAKE_USER_ID)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.communication.schemas.communication import (
    NotificationTemplateResponse, NotificationTemplateCreate,
    NotificationResponse, NotificationPublishEvent,
    CommunicationPreferenceResponse, CommunicationPreferenceBase
)
from app.communication.models.communication import NotificationTemplate, TemplateVersion, CommunicationPreference
from app.communication.repositories.communication_repo import CommunicationRepository
from app.communication.services.communication_service import CommunicationService
from app.identity.middleware.auth_middleware import get_current_user
from app.identity.schemas.user import UserResponse

router = APIRouter(prefix="/communication", tags=["Communication"])

@router.post("/notifications", response_model=NotificationResponse)
def publish_notification(
    payload: NotificationPublishEvent,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Publish a new notification event manually"""
    svc = CommunicationService(db)
    notification = svc.publish_event(
        event_type=payload.event_type,
        payload=payload.payload,
        user_id=payload.recipient_user_id,
        email=payload.recipient_email,
        phone=payload.recipient_phone,
        force_channel=payload.channel
    )
    return notification

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get notifications for the current user"""
    from app.communication.models.communication import CommunicationNotification
    notifications = db.query(CommunicationNotification).filter(CommunicationNotification.recipient_user_id == current_user.id).offset(skip).limit(limit).all()
    return notifications

@router.get("/preferences", response_model=CommunicationPreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get communication preferences for the current user"""
    repo = CommunicationRepository(db)
    pref = repo.get_preference(current_user.id)
    if not pref:
        pref = CommunicationPreference(user_id=current_user.id)
        repo.set_preference(pref)
    return pref

@router.patch("/preferences", response_model=CommunicationPreferenceResponse)
def update_preferences(
    payload: CommunicationPreferenceBase,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update communication preferences for the current user"""
    repo = CommunicationRepository(db)
    pref = CommunicationPreference(user_id=current_user.id, **payload.model_dump())
    return repo.set_preference(pref)

@router.post("/templates", response_model=NotificationTemplateResponse)
def create_template(
    payload: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new notification template (admin/org only in real system)"""
    repo = CommunicationRepository(db)
    template = NotificationTemplate(
        name=payload.name,
        description=payload.description,
        channel=payload.channel,
        is_active=payload.is_active
    )
    
    version = TemplateVersion(
        version=payload.initial_version.version,
        subject_template=payload.initial_version.subject_template,
        body_template=payload.initial_version.body_template,
        is_published=payload.initial_version.is_published
    )
    template.versions = [version]
    
    return repo.create_template(template)

@router.get("/queue/status")
def get_queue_status(db: Session = Depends(get_db)):
    """Get basic queue status metrics"""
    from app.communication.models.communication import NotificationQueue
    from sqlalchemy import func
    status_counts = db.query(NotificationQueue.status, func.count(NotificationQueue.id)).group_by(NotificationQueue.status).all()
    return {status: count for status, count in status_counts}

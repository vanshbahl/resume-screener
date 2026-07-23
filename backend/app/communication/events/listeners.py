import logging
from typing import Dict, Any
from app.core.database import SessionLocal
from app.communication.services.communication_service import CommunicationService
from app.workflow.events.sync import SyncEventBus # Assuming this exists or similar

logger = logging.getLogger(__name__)

def handle_candidate_created(event_data: Dict[str, Any]):
    logger.info(f"Handling CandidateCreated for Communication Hub: {event_data}")
    db = SessionLocal()
    try:
        svc = CommunicationService(db)
        # Notify recruiters or candidate
        svc.publish_event(
            event_type="CandidateCreated",
            payload=event_data,
            email=event_data.get("email"),
            force_channel="EMAIL"
        )
    finally:
        db.close()

def handle_interview_scheduled(event_data: Dict[str, Any]):
    logger.info(f"Handling InterviewScheduled for Communication Hub: {event_data}")
    db = SessionLocal()
    try:
        svc = CommunicationService(db)
        svc.publish_event(
            event_type="InterviewScheduled",
            payload=event_data,
            user_id=event_data.get("interviewer_id"),
            force_channel="EMAIL"
        )
    finally:
        db.close()

def register_communication_listeners():
    # Attempt to bind to existing SyncEventBus if it exists
    try:
        SyncEventBus.subscribe("CandidateCreated", handle_candidate_created)
        SyncEventBus.subscribe("InterviewScheduled", handle_interview_scheduled)
        logger.info("Communication event listeners registered successfully.")
    except Exception as e:
        logger.warning(f"Could not register communication listeners (SyncEventBus might not be fully initialized or missing): {e}")

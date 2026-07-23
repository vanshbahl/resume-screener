import pytest
from sqlalchemy.orm import Session
from app.communication.models.communication import (
    NotificationTemplate, TemplateVersion, CommunicationPreference, CommunicationNotification, NotificationStatus, NotificationQueue
)
from app.communication.repositories.communication_repo import CommunicationRepository
from app.communication.services.communication_service import TemplateService, PreferenceService, DeliveryService, CommunicationService
from app.communication.api.router import get_current_user

def test_template_rendering():
    from app.communication.templates.engine import Jinja2TemplateEngine
    engine = Jinja2TemplateEngine()
    result = engine.render("Hello {{ name }}, your role is {{ role }}.", {"name": "Alice", "role": "Engineer"})
    assert result == "Hello Alice, your role is Engineer."

def test_preference_override():
    from app.communication.models.communication import CommunicationPreference
    pref = CommunicationPreference(user_id=1, enable_email=False, enable_sms=True, enable_push=True)
    
    # We can mock repo or just test service logic
    from app.communication.services.communication_service import PreferenceService
    svc = PreferenceService(None)
    assert svc.should_deliver(pref, "EMAIL") == False
    assert svc.should_deliver(pref, "SMS") == True
    assert svc.should_deliver(pref, "PUSH") == True # default is True from our PreferenceService logic if not explicitly checked as False but pref has it as True by default in model. Wait, the model default is True.

def test_queue_processing(db_session: Session):
    from sqlalchemy import inspect
    inspector = inspect(db_session.get_bind())
    print("DB TABLES IN POSTGRES:", inspector.get_table_names())
    repo = CommunicationRepository(db_session)
    svc = CommunicationService(db_session)
    
    # Create a template
    template = NotificationTemplate(name="Welcome", channel="EMAIL")
    version = TemplateVersion(version=1, body_template="Welcome {{ user }}!", is_published=True)
    template.versions.append(version)
    repo.create_template(template)
    
    # Publish event
    notification = svc.publish_event("UserWelcome", {"user": "Bob"}, email="bob@example.com")
    assert notification.status == NotificationStatus.QUEUED
    
    # Process queue
    from app.communication.queue.processor import QueueProcessor
    processor = QueueProcessor(batch_size=10, max_retries=1)
    processor.process_batch(db=db_session)

    # Verify items processed
    queue_items = repo.get_pending_queue_items(limit=10)
    
    # Verify
    db_session.refresh(notification)
    assert notification.status == NotificationStatus.DELIVERED
    
    attempts = notification.attempts
    assert len(attempts) == 1
    assert attempts[0].status == "SUCCESS"
    assert attempts[0].provider == "MockEmail"

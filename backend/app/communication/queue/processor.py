import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.communication.models.communication import QueueStatus
from app.communication.repositories.communication_repo import CommunicationRepository
from app.communication.services.communication_service import DeliveryService

logger = logging.getLogger(__name__)

class QueueProcessor:
    def __init__(self, batch_size: int = 50, max_retries: int = 3):
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("Notification Queue Processor started.")
        while self.is_running:
            try:
                self.process_batch()
            except Exception as e:
                logger.error(f"Error in QueueProcessor: {e}")
            await asyncio.sleep(5) # Poll interval
            
    def stop(self):
        self.is_running = False
        logger.info("Notification Queue Processor stopped.")

    def process_batch(self, db: Optional[Session] = None):
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            repo = CommunicationRepository(db)
            delivery_svc = DeliveryService(repo)
            
            pending_items = repo.get_pending_queue_items(limit=self.batch_size)
            if not pending_items:
                return
                
            logger.info(f"Processing {len(pending_items)} queued notifications")
            for item in pending_items:
                item.status = QueueStatus.PROCESSING
                repo.update_queue_item(item)
                
                success = delivery_svc.process_notification(item.notification_id)
                if success:
                    item.status = QueueStatus.COMPLETED
                else:
                    item.retry_count += 1
                    if item.retry_count >= self.max_retries:
                        item.status = QueueStatus.DEAD_LETTER
                    else:
                        item.status = QueueStatus.RETRY
                        # In real system, set next_retry_at here based on exponential backoff
                
                repo.update_queue_item(item)
        finally:
            if close_db:
                db.close()

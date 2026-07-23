from typing import List
from sqlalchemy.orm import Session
from app.workflow.models.workflow import WorkflowTimeline
from app.workspace.schemas.workspace import ActivityFeedItem

class ActivityFeedService:
    def __init__(self, db: Session):
        self.db = db

    def get_global_activity_feed(self, limit: int = 50, offset: int = 0) -> List[ActivityFeedItem]:
        # Aggregate timeline events from the workflow domain
        events = self.db.query(WorkflowTimeline).order_by(
            WorkflowTimeline.timestamp.desc()
        ).offset(offset).limit(limit).all()
        
        feed = []
        for event in events:
            feed.append(ActivityFeedItem(
                id=str(event.id),
                domain="workflow",
                event_type=event.event_type,
                details=event.details or {},
                timestamp=event.timestamp,
                user_id=event.user_id
            ))
            
        return feed

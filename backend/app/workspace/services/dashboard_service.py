from sqlalchemy.orm import Session
from sqlalchemy import func
from app.job.models.job import Job
from app.workflow.models.workflow import WorkflowInstance, WorkflowTimeline
from app.workspace.schemas.workspace import DashboardSummary
from app.workspace.caching.base import CacheRepository
from app.workspace.caching.memory import memory_cache

class DashboardService:
    def __init__(self, db: Session, cache: CacheRepository = memory_cache):
        self.db = db
        self.cache = cache

    def get_dashboard_summary(self, user_id: str) -> DashboardSummary:
        cache_key = f"dashboard_summary_{user_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return DashboardSummary(**cached)

        # Calculate Open Jobs
        open_jobs = self.db.query(func.count(Job.id)).filter(Job.status == "OPEN").scalar() or 0
        
        # Calculate Assigned Candidates (Simplified: candidates that exist or mapped to active pipelines)
        # Assuming we just count total active pipelines for this user's jobs or general active candidates.
        # For this example, we count active pipeline instances:
        assigned_candidates = self.db.query(func.count(WorkflowInstance.id)).filter(
            WorkflowInstance.status == "active"
        ).scalar() or 0
        
        # Pending Approvals (Example: pipeline instances in 'OFFER_PENDING' or similar)
        # Using a generic stat here
        pending_approvals = self.db.query(func.count(WorkflowInstance.id)).filter(
            # Usually we'd join with stages or approvals. Simplified for MVP:
            WorkflowInstance.status == "active" 
        ).scalar() or 0

        # Recent activity count (timeline events in last 24h)
        # Simplification: just counting total events for demonstration.
        recent_activity_count = self.db.query(func.count(WorkflowTimeline.id)).scalar() or 0

        summary = DashboardSummary(
            open_jobs=open_jobs,
            assigned_candidates=assigned_candidates,
            interviews_today=0, # Would query a calendar/interview model
            pending_approvals=pending_approvals,
            recent_activity_count=recent_activity_count
        )

        self.cache.set(cache_key, summary.model_dump(), ttl_seconds=60)
        return summary

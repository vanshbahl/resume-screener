from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.candidate.models.candidate import Candidate
from app.job.models.job import Job
from app.workflow.models.workflow import WorkflowInstance, WorkflowTimeline
from app.interview.models.interview import Interview, InterviewFeedback
from app.analytics.models.analytics import DashboardConfig, SavedReport

class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Configurations
    # ---------------------------------------------------------
    def get_dashboard_config(self, user_id: str, dashboard_type: str) -> Optional[DashboardConfig]:
        return self.db.query(DashboardConfig).filter(
            DashboardConfig.user_id == user_id,
            DashboardConfig.dashboard_type == dashboard_type
        ).first()

    def save_dashboard_config(self, user_id: str, dashboard_type: str, widgets: List[Dict[str, Any]]) -> DashboardConfig:
        config = self.get_dashboard_config(user_id, dashboard_type)
        if config:
            config.widgets = widgets
        else:
            config = DashboardConfig(user_id=user_id, dashboard_type=dashboard_type, widgets=widgets)
            self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    # ---------------------------------------------------------
    # Core Aggregations for KPIs
    # ---------------------------------------------------------
    def get_total_candidates(self) -> int:
        return self.db.query(func.count(Candidate.id)).scalar() or 0

    def get_active_jobs(self) -> int:
        return self.db.query(func.count(Job.id)).filter(Job.status == "PUBLISHED").scalar() or 0

    def get_workflow_conversions(self, target_status: str = "hired") -> int:
        return self.db.query(func.count(WorkflowInstance.id)).filter(
            WorkflowInstance.status == target_status
        ).scalar() or 0

    def get_average_time_to_hire_days(self) -> float:
        # Time to hire = Workflow created_at to Workflow status == hired updated_at
        # In a real enterprise system, we'd query the Timeline events.
        # For simplicity, we just use the difference between updated_at and created_at for 'hired' workflows.
        # SQLite doesn't natively support easy date diffs in SQLAlchemy generic func. 
        # Since we use Postgres in tests, we can use extract epoch or just fetch and compute in Python for cross-db safety.
        
        # Cross-db safe python calculation for MVP:
        workflows = self.db.query(WorkflowInstance).filter(WorkflowInstance.status == "hired").all()
        if not workflows:
            return 0.0
            
        total_days = 0.0
        for w in workflows:
            diff = w.updated_at - w.created_at
            total_days += diff.total_seconds() / 86400.0
            
        return round(total_days / len(workflows), 1)

    def get_offer_acceptance_rate(self) -> float:
        # Assuming "offer_accepted" vs "offer_rejected" status or timeline events.
        # For now, let's use dummy calculation based on total workflows to hired.
        total_terminal = self.db.query(func.count(WorkflowInstance.id)).filter(
            WorkflowInstance.status.in_(["hired", "rejected", "withdrawn"])
        ).scalar() or 0
        
        if total_terminal == 0:
            return 0.0
            
        hired = self.get_workflow_conversions("hired")
        return round((hired / total_terminal) * 100, 1)

    # ---------------------------------------------------------
    # Time-Series Trends
    # ---------------------------------------------------------
    def get_hiring_trend_last_n_days(self, days: int = 30) -> List[Dict[str, Any]]:
        # Fetch all hired workflows in the last N days
        cutoff = datetime.utcnow() - timedelta(days=days)
        workflows = self.db.query(WorkflowInstance.updated_at).filter(
            WorkflowInstance.status == "hired",
            WorkflowInstance.updated_at >= cutoff
        ).all()
        
        # Aggregate in Python for cross-db compatibility (SQLite/Postgres)
        counts_by_date = {}
        for (updated_at,) in workflows:
            date_str = updated_at.strftime("%Y-%m-%d")
            counts_by_date[date_str] = counts_by_date.get(date_str, 0) + 1
            
        # Ensure all days are represented
        results = []
        for i in range(days):
            dt = (cutoff + timedelta(days=i)).strftime("%Y-%m-%d")
            results.append({"date": dt, "value": counts_by_date.get(dt, 0)})
            
        return results

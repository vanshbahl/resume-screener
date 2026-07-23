from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from app.analytics.repositories.analytics_repo import AnalyticsRepository
from app.analytics.schemas.analytics import DashboardConfigCreate, DashboardConfigResponse

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalyticsRepository(db)

    def get_dashboard_config(self, user_id: str, dashboard_type: str) -> Optional[DashboardConfigResponse]:
        config = self.repo.get_dashboard_config(user_id, dashboard_type)
        if config:
            return DashboardConfigResponse.model_validate(config)
        return None

    def save_dashboard_config(self, user_id: str, data: DashboardConfigCreate) -> DashboardConfigResponse:
        config = self.repo.save_dashboard_config(user_id, data.dashboard_type, data.widgets)
        return DashboardConfigResponse.model_validate(config)


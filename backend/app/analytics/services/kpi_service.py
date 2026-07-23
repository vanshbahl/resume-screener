from sqlalchemy.orm import Session
from typing import List
from app.analytics.repositories.analytics_repo import AnalyticsRepository
from app.analytics.schemas.analytics import KPIResponse, KPIValue

class KPIService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalyticsRepository(db)

    def get_core_kpis(self) -> KPIResponse:
        kpis = [
            KPIValue(
                name="Total Candidates",
                value=self.repo.get_total_candidates(),
                unit="count"
            ),
            KPIValue(
                name="Active Jobs",
                value=self.repo.get_active_jobs(),
                unit="count"
            ),
            KPIValue(
                name="Total Hired",
                value=self.repo.get_workflow_conversions("hired"),
                unit="count"
            ),
            KPIValue(
                name="Avg Time To Hire",
                value=self.repo.get_average_time_to_hire_days(),
                unit="days"
            ),
            KPIValue(
                name="Offer Acceptance Rate",
                value=self.repo.get_offer_acceptance_rate(),
                unit="%"
            )
        ]
        return KPIResponse(kpis=kpis)

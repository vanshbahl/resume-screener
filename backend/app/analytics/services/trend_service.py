from sqlalchemy.orm import Session
from app.analytics.repositories.analytics_repo import AnalyticsRepository
from app.analytics.schemas.analytics import TrendResponse, TrendPoint

class TrendService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalyticsRepository(db)

    def get_hiring_trends(self, days: int = 30) -> TrendResponse:
        raw_data = self.repo.get_hiring_trend_last_n_days(days)
        points = [TrendPoint(date=d["date"], value=d["value"]) for d in raw_data]
        return TrendResponse(
            metric_name="Hires Over Time",
            data_points=points
        )

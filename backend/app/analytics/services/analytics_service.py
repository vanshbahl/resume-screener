from sqlalchemy.orm import Session
from app.analytics.services.kpi_service import KPIService
from app.analytics.services.trend_service import TrendService
from app.analytics.services.dashboard_service import DashboardService
from app.analytics.services.report_service import ReportService
from app.analytics.services.export_service import ExportService
from app.workspace.caching.memory import MemoryCacheRepository
from app.analytics.schemas.analytics import KPIResponse

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.kpi_svc = KPIService(db)
        self.trend_svc = TrendService(db)
        self.dashboard_svc = DashboardService(db)
        self.report_svc = ReportService(db)
        self.export_svc = ExportService()
        self.cache = MemoryCacheRepository() # Shared caching interface

    def get_core_kpis(self) -> KPIResponse:
        cache_key = "analytics:core_kpis"
        cached = self.cache.get(cache_key)
        if cached:
            return KPIResponse.model_validate(cached)
            
        kpis = self.kpi_svc.get_core_kpis()
        self.cache.set(cache_key, kpis.model_dump(), ttl_seconds=300) # 5 min cache
        return kpis

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.analytics.schemas.analytics import (
    KPIResponse, TrendResponse, ReportFilter, ReportResponse, 
    DashboardConfigCreate, DashboardConfigResponse
)
from app.analytics.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])

# Mock User ID for auth bypass
FAKE_USER_ID = "recruiter_001"

@router.get("/kpis", response_model=KPIResponse)
def get_kpis(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.get_core_kpis()

@router.get("/trends", response_model=TrendResponse)
def get_hiring_trends(days: int = 30, db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.trend_svc.get_hiring_trends(days)

@router.post("/reports/candidate", response_model=ReportResponse)
def get_candidate_report(filters: ReportFilter, db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.report_svc.generate_candidate_report(filters)

@router.post("/reports/candidate/export", response_class=PlainTextResponse)
def export_candidate_report(filters: ReportFilter, db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    report = svc.report_svc.generate_candidate_report(filters)
    csv_data = svc.export_svc.export_report_to_csv(report)
    return PlainTextResponse(content=csv_data, media_type="text/csv")

@router.get("/dashboard/{dashboard_type}", response_model=DashboardConfigResponse)
def get_dashboard_config(dashboard_type: str, db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    config = svc.dashboard_svc.get_dashboard_config(FAKE_USER_ID, dashboard_type)
    if not config:
        raise HTTPException(status_code=404, detail="Dashboard config not found")
    return config

@router.post("/dashboard", response_model=DashboardConfigResponse)
def save_dashboard_config(data: DashboardConfigCreate, db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.dashboard_svc.save_dashboard_config(FAKE_USER_ID, data)

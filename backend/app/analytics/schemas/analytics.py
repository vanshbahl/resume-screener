from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime

# ---------------------------------------------------------
# KPI Schemas
# ---------------------------------------------------------
class KPIValue(BaseModel):
    name: str
    value: float
    unit: str
    trend_percentage: Optional[float] = None # e.g., +5.2% from last period

class KPIResponse(BaseModel):
    kpis: List[KPIValue]

# ---------------------------------------------------------
# Trend & Chart Schemas
# ---------------------------------------------------------
class TrendPoint(BaseModel):
    date: str # ISO Date or label
    value: float

class TrendResponse(BaseModel):
    metric_name: str
    data_points: List[TrendPoint]

# ---------------------------------------------------------
# Report Schemas
# ---------------------------------------------------------
class ReportFilter(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    department: Optional[str] = None
    recruiter_id: Optional[str] = None
    job_id: Optional[str] = None
    candidate_id: Optional[str] = None
    status: Optional[str] = None

class ReportResponse(BaseModel):
    report_name: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_count: int

# ---------------------------------------------------------
# Config Schemas
# ---------------------------------------------------------
class DashboardConfigCreate(BaseModel):
    dashboard_type: str
    widgets: List[Dict[str, Any]]

class DashboardConfigResponse(BaseModel):
    id: str
    user_id: str
    dashboard_type: str
    widgets: List[Dict[str, Any]]
    
    model_config = {"from_attributes": True}

class SavedReportCreate(BaseModel):
    name: str
    report_type: str
    filters: Dict[str, Any]

class SavedReportResponse(BaseModel):
    id: str
    name: str
    report_type: str
    filters: Dict[str, Any]
    
    model_config = {"from_attributes": True}

"""Pydantic schemas for Report resources."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.report import ReportStatus
from app.schemas.parameter import ParameterOut, RecommendationOut


class ReportSummary(BaseModel):
    id: str
    title: str
    status: ReportStatus
    health_score: Optional[float]
    risk_category: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportDetail(ReportSummary):
    ai_summary: Optional[str]
    raw_extracted_text: Optional[str]
    parameters: List[ParameterOut] = []
    recommendations: List[RecommendationOut] = []

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ReportSummary]


class DashboardStats(BaseModel):
    total_reports: int
    average_health_score: Optional[float]
    abnormal_parameter_count: int
    latest_report_id: Optional[str]
    trend: List[dict]

"""Dashboard aggregate statistics endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.parameter import ExtractedParameter, ParameterFlag
from app.models.report import Report
from app.models.user import User
from app.repositories.report_repository import ReportRepository
from app.schemas.report import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ReportRepository(db)
    reports, total = repo.list_for_user(current_user.id, skip=0, limit=1000)

    abnormal_count = (
        db.query(ExtractedParameter)
        .join(Report)
        .filter(
            Report.owner_id == current_user.id,
            ExtractedParameter.flag.notin_([ParameterFlag.NORMAL, ParameterFlag.UNKNOWN]),
        )
        .count()
    )

    trend = [
        {"report_id": r.id, "date": r.created_at.isoformat(), "health_score": r.health_score}
        for r in sorted(reports, key=lambda r: r.created_at)
        if r.health_score is not None
    ]

    return DashboardStats(
        total_reports=total,
        average_health_score=repo.average_health_score(current_user.id),
        abnormal_parameter_count=abnormal_count,
        latest_report_id=reports[0].id if reports else None,
        trend=trend,
    )

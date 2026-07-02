"""Report retrieval, listing/search, and PDF export endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportDetail, ReportListResponse, ReportSummary
from app.services.report_service import ReportService
from app.utils.pdf_utils import generate_report_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=ReportListResponse)
def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search reports by title"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ReportRepository(db)
    items, total = repo.list_for_user(
        current_user.id, skip=(page - 1) * page_size, limit=page_size, search=search
    )
    return ReportListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{report_id}", response_model=ReportDetail)
def get_report(report_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = ReportService(db)
    return service.get_report_for_user(report_id, current_user.id)


@router.delete("/{report_id}", status_code=204)
def delete_report(report_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = ReportService(db)
    service.delete_report(report_id, current_user.id)


@router.get("/{report_id}/export/pdf")
def export_report_pdf(report_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = ReportService(db)
    report = service.get_report_for_user(report_id, current_user.id)
    pdf_bytes = generate_report_pdf(report)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{report_id}.pdf"'},
    )

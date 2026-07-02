"""Report upload endpoint — accepts a file, stores it, and triggers analysis."""
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.report import ReportSummary
from app.services.report_service import ReportService
from app.utils.file_utils import generate_storage_path, save_upload_bytes, validate_upload

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("", response_model=ReportSummary, status_code=201)
async def upload_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    validate_upload(file.filename, len(contents))
    storage_path = generate_storage_path(file.filename)
    save_upload_bytes(contents, storage_path)

    service = ReportService(db)
    report = service.create_report_from_upload(
        owner_id=current_user.id,
        original_filename=file.filename,
        storage_path=storage_path,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(contents),
    )

    # Analysis is dispatched as a background task so the client gets an
    # immediate response; poll GET /reports/{id} for status updates.
    background_tasks.add_task(service.process_report, report.id)
    return report

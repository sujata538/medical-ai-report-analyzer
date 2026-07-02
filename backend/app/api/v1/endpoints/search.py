"""Search endpoint: full-text-ish search across a user's reports and extracted parameters."""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.parameter import ExtractedParameter
from app.models.report import Report
from app.models.user import User

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
def search(
    q: str = Query(..., min_length=1, description="Search term"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    matching_reports = (
        db.query(Report)
        .filter(Report.owner_id == current_user.id, Report.title.ilike(f"%{q}%"))
        .all()
    )

    matching_parameters = (
        db.query(ExtractedParameter)
        .join(Report)
        .filter(Report.owner_id == current_user.id, ExtractedParameter.name.ilike(f"%{q}%"))
        .all()
    )

    return {
        "reports": [{"id": r.id, "title": r.title, "created_at": r.created_at} for r in matching_reports],
        "parameters": [
            {
                "id": p.id, "report_id": p.report_id, "name": p.name,
                "value": p.value, "unit": p.unit, "flag": p.flag.value,
            }
            for p in matching_parameters
        ],
    }

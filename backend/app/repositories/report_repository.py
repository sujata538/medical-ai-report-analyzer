"""Repository for Report persistence + query operations."""
from typing import Optional, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.report import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    def __init__(self, db: Session):
        super().__init__(Report, db)

    def get_with_details(self, report_id: str) -> Optional[Report]:
        return (
            self.db.query(Report)
            .options(joinedload(Report.parameters), joinedload(Report.recommendations))
            .filter(Report.id == report_id)
            .first()
        )

    def list_for_user(
        self, owner_id: str, skip: int = 0, limit: int = 20, search: Optional[str] = None
    ) -> Tuple[List[Report], int]:
        query = self.db.query(Report).filter(Report.owner_id == owner_id)
        if search:
            query = query.filter(Report.title.ilike(f"%{search}%"))
        total = query.count()
        items = (
            query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
        )
        return items, total

    def average_health_score(self, owner_id: str) -> Optional[float]:
        result = (
            self.db.query(func.avg(Report.health_score))
            .filter(Report.owner_id == owner_id, Report.health_score.isnot(None))
            .scalar()
        )
        return float(result) if result is not None else None

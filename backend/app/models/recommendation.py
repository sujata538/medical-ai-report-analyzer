"""
Recommendation model.

Stores cautious, educational (never diagnostic) recommendations generated
by the recommendation engine for a given report/parameter combination.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class RecommendationSeverity(str, enum.Enum):
    INFO = "info"
    ADVISORY = "advisory"
    IMPORTANT = "important"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id"), nullable=False)

    parameter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[RecommendationSeverity] = mapped_column(
        SAEnum(RecommendationSeverity), default=RecommendationSeverity.INFO
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    report: Mapped["Report"] = relationship(back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<Recommendation {self.parameter_name} severity={self.severity}>"

"""
Report model.

A `Report` represents a single lab/pathology report uploaded by a user. It
aggregates the uploaded file, extracted parameters, AI-generated summary,
and computed health score.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class ReportStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    ANALYZED = "analyzed"
    FAILED = "failed"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), default="Untitled Report")
    report_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(SAEnum(ReportStatus), default=ReportStatus.UPLOADED)

    raw_extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    health_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    owner: Mapped["User"] = relationship(back_populates="reports")
    files: Mapped[list["UploadedFile"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    parameters: Mapped[list["ExtractedParameter"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Report id={self.id} status={self.status}>"

"""
Extracted lab parameter model.

Each row is a single lab value pulled out of a report (e.g. "Hemoglobin:
13.5 g/dL"), linked to a reference range for interpretation.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class ParameterFlag(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL_LOW = "critical_low"
    CRITICAL_HIGH = "critical_high"
    UNKNOWN = "unknown"


class ExtractedParameter(Base):
    __tablename__ = "extracted_parameters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id"), nullable=False)
    reference_range_id: Mapped[int | None] = mapped_column(
        ForeignKey("reference_ranges.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(String(500), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    flag: Mapped[ParameterFlag] = mapped_column(SAEnum(ParameterFlag), default=ParameterFlag.UNKNOWN)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 - 1.0

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    report: Mapped["Report"] = relationship(back_populates="parameters")
    reference_range: Mapped["ReferenceRange"] = relationship(back_populates="parameters")

    def __repr__(self) -> str:
        return f"<Parameter {self.name}={self.value}{self.unit or ''} flag={self.flag}>"

"""
Reference range model.

Holds the clinically-normal min/max for a given lab parameter, optionally
segmented by sex and age band, used by the reference-range service to flag
extracted values as low/normal/high.
"""
from __future__ import annotations

from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReferenceRange(Base):
    __tablename__ = "reference_ranges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parameter_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)

    sex: Mapped[str] = mapped_column(String(10), default="any")  # male | female | any
    min_age: Mapped[int] = mapped_column(Integer, default=0)
    max_age: Mapped[int] = mapped_column(Integer, default=120)

    low: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    critical_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    critical_high: Mapped[float | None] = mapped_column(Float, nullable=True)

    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    parameters: Mapped[list["ExtractedParameter"]] = relationship(back_populates="reference_range")

    def __repr__(self) -> str:
        return f"<ReferenceRange {self.parameter_name} [{self.low}-{self.high}]{self.unit}>"

"""
Reference range service.

Provides:
    - `seed_reference_ranges()`: populate the DB with commonly used adult
      reference ranges (general-population defaults; not sex/age specific
      beyond what's noted — a real clinical deployment should source these
      from a validated lab reference database).
    - `flag_value()`: given a parameter name + numeric value, look up the
      matching ReferenceRange row and return the appropriate ParameterFlag.
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.parameter import ParameterFlag
from app.models.reference_range import ReferenceRange

logger = logging.getLogger(__name__)

# (name, unit, low, high, critical_low, critical_high)
DEFAULT_RANGES = [
    ("Hemoglobin", "g/dL", 13.0, 17.0, 7.0, 20.0),
    ("Hematocrit", "%", 38.0, 50.0, 20.0, 60.0),
    ("WBC Count", "/uL", 4000, 11000, 2000, 30000),
    ("RBC Count", "/uL", 4.2, 5.9, 2.5, 7.5),
    ("Platelet Count", "/uL", 150000, 450000, 20000, 1000000),
    ("Glucose", "mg/dL", 70, 99, 40, 400),
    ("Fasting Glucose", "mg/dL", 70, 99, 40, 400),
    ("HbA1c", "%", 4.0, 5.6, None, 14.0),
    ("Total Cholesterol", "mg/dL", 125, 200, None, 400),
    ("LDL Cholesterol", "mg/dL", 0, 100, None, 300),
    ("HDL Cholesterol", "mg/dL", 40, 60, 20, None),
    ("Triglycerides", "mg/dL", 0, 150, None, 500),
    ("Creatinine", "mg/dL", 0.6, 1.3, 0.2, 10.0),
    ("Blood Urea Nitrogen", "mg/dL", 7, 20, 2, 100),
    ("Sodium", "mEq/L", 135, 145, 120, 160),
    ("Potassium", "mEq/L", 3.5, 5.1, 2.5, 6.5),
    ("TSH", "mIU/L", 0.4, 4.0, 0.01, 100),
    ("Vitamin D", "ng/mL", 30, 100, 10, 150),
    ("Vitamin B12", "pg/mL", 200, 900, 100, 2000),
    ("Ferritin", "ng/mL", 20, 250, 5, 1000),
    ("Uric Acid", "mg/dL", 3.4, 7.2, 1.0, 15.0),
    ("CRP", "mg/dL", 0, 1.0, None, 20.0),
]


def seed_reference_ranges(db: Session) -> None:
    for name, unit, low, high, crit_low, crit_high in DEFAULT_RANGES:
        exists = db.query(ReferenceRange).filter(ReferenceRange.parameter_name == name).first()
        if exists:
            continue
        db.add(
            ReferenceRange(
                parameter_name=name, unit=unit, low=low, high=high,
                critical_low=crit_low, critical_high=crit_high, sex="any",
            )
        )
    db.commit()
    logger.info("Seeded %d default reference ranges.", len(DEFAULT_RANGES))


class ReferenceRangeService:
    def __init__(self, db: Session):
        self.db = db

    def get_range(self, parameter_name: str) -> Optional[ReferenceRange]:
        return (
            self.db.query(ReferenceRange)
            .filter(ReferenceRange.parameter_name.ilike(parameter_name))
            .first()
        )

    def flag_value(self, parameter_name: str, value: float) -> tuple[ParameterFlag, Optional[ReferenceRange]]:
        ref = self.get_range(parameter_name)
        if not ref:
            return ParameterFlag.UNKNOWN, None

        if ref.critical_low is not None and value <= ref.critical_low:
            return ParameterFlag.CRITICAL_LOW, ref
        if ref.critical_high is not None and value >= ref.critical_high:
            return ParameterFlag.CRITICAL_HIGH, ref
        if value < ref.low:
            return ParameterFlag.LOW, ref
        if value > ref.high:
            return ParameterFlag.HIGH, ref
        return ParameterFlag.NORMAL, ref

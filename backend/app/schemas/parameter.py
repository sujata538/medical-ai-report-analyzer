"""Pydantic schemas for extracted lab parameters."""
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.parameter import ParameterFlag


class ParameterOut(BaseModel):
    id: str
    name: str
    raw_text: str
    value: float
    unit: Optional[str]
    flag: ParameterFlag
    confidence: float
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class RecommendationOut(BaseModel):
    id: str
    parameter_name: Optional[str]
    message: str
    severity: str

    model_config = ConfigDict(from_attributes=True)

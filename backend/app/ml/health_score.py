"""
Health score module.

Computes a single 0-100 "health score" for a report from its flagged
parameters, plus a coarse risk category. This is a transparent, rule-based
weighted scoring model (NOT a diagnostic model) — every parameter that is
outside its reference range subtracts points proportional to how far out
of range it is and how clinically significant that parameter is judged to
be, via `PARAMETER_WEIGHTS`.

The `Explainability` module (app/ml/explainability.py) can attribute the
score back to individual parameters (SHAP-style) for the "why did I get
this score" UI.
"""
from __future__ import annotations

from typing import Iterable, List, Tuple

from app.models.parameter import ParameterFlag

# Relative clinical importance per parameter (defaults to 1.0 if absent).
# Tuned conservatively; intended as a reasonable starting point, not medical fact.
PARAMETER_WEIGHTS = {
    "Hemoglobin": 1.5,
    "Glucose": 1.5,
    "Fasting Glucose": 1.5,
    "HbA1c": 1.8,
    "LDL Cholesterol": 1.4,
    "HDL Cholesterol": 1.2,
    "Triglycerides": 1.2,
    "Creatinine": 1.6,
    "Blood Urea Nitrogen": 1.3,
    "TSH": 1.3,
    "Platelet Count": 1.4,
    "WBC Count": 1.3,
}

FLAG_PENALTY = {
    ParameterFlag.NORMAL: 0.0,
    ParameterFlag.LOW: 4.0,
    ParameterFlag.HIGH: 4.0,
    ParameterFlag.CRITICAL_LOW: 10.0,
    ParameterFlag.CRITICAL_HIGH: 10.0,
    ParameterFlag.UNKNOWN: 0.0,
}


def compute_health_score(parameter_flags: Iterable[Tuple[str, ParameterFlag]]) -> float:
    """
    Start at 100 and deduct weighted penalties for each abnormal parameter.
    Floors at 0. Returns a float rounded to 1 decimal place.
    """
    score = 100.0
    for name, flag in parameter_flags:
        weight = PARAMETER_WEIGHTS.get(name, 1.0)
        score -= FLAG_PENALTY.get(flag, 0.0) * weight

    return round(max(score, 0.0), 1)


def categorize_risk(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 55:
        return "moderate"
    if score >= 35:
        return "elevated"
    return "high"


def score_breakdown(parameter_flags: List[Tuple[str, ParameterFlag]]) -> List[dict]:
    """Per-parameter contribution to the deduction, for transparency in the UI."""
    breakdown = []
    for name, flag in parameter_flags:
        weight = PARAMETER_WEIGHTS.get(name, 1.0)
        penalty = FLAG_PENALTY.get(flag, 0.0) * weight
        breakdown.append({"parameter": name, "flag": flag.value, "score_impact": -round(penalty, 1)})
    return sorted(breakdown, key=lambda x: x["score_impact"])

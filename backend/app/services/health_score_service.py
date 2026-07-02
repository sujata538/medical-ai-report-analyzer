"""
Health score service.

Thin orchestration layer around `app.ml.health_score` that works directly
with ORM `ExtractedParameter` objects.
"""
from __future__ import annotations

from typing import List

from app.ml.explainability import Explainability
from app.ml.health_score import categorize_risk, compute_health_score
from app.models.parameter import ExtractedParameter


class HealthScoreService:
    def __init__(self):
        self.explainability = Explainability()

    def score_report(self, parameters: List[ExtractedParameter]) -> dict:
        pairs = [(p.name, p.flag) for p in parameters]
        score = compute_health_score(pairs)
        risk = categorize_risk(score)
        breakdown = self.explainability.explain_health_score(pairs)
        return {
            "health_score": score,
            "risk_category": risk,
            "breakdown": breakdown,
            "explainability_note": self.explainability.confidence_note(),
        }

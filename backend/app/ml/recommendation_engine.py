"""
Recommendation engine.

Generates cautious, educational (never diagnostic) recommendations from
flagged parameters. Every message is deliberately hedged and steers the
user toward a clinician rather than asserting a medical conclusion.

This is a template/rule-based engine. `AIService` (app/services/ai_service.py)
may further polish these with an LLM if configured, but the engine here is
the safety-reviewed source of truth for *content*, so an LLM should only be
used to reword — never to add new claims.
"""
from __future__ import annotations

from typing import List

from app.models.parameter import ParameterFlag
from app.models.recommendation import RecommendationSeverity

_TEMPLATES = {
    ParameterFlag.HIGH: (
        "Your {name} value came back above the typical reference range. "
        "This can happen for many reasons and isn't a diagnosis on its own — "
        "consider discussing this result with a healthcare provider for context."
    ),
    ParameterFlag.LOW: (
        "Your {name} value came back below the typical reference range. "
        "This can happen for many reasons and isn't a diagnosis on its own — "
        "consider discussing this result with a healthcare provider for context."
    ),
    ParameterFlag.CRITICAL_HIGH: (
        "Your {name} value is significantly above the typical reference range. "
        "We'd strongly encourage reviewing this result with a healthcare provider "
        "soon so it can be properly interpreted in the context of your health history."
    ),
    ParameterFlag.CRITICAL_LOW: (
        "Your {name} value is significantly below the typical reference range. "
        "We'd strongly encourage reviewing this result with a healthcare provider "
        "soon so it can be properly interpreted in the context of your health history."
    ),
}

_SEVERITY_MAP = {
    ParameterFlag.HIGH: RecommendationSeverity.ADVISORY,
    ParameterFlag.LOW: RecommendationSeverity.ADVISORY,
    ParameterFlag.CRITICAL_HIGH: RecommendationSeverity.IMPORTANT,
    ParameterFlag.CRITICAL_LOW: RecommendationSeverity.IMPORTANT,
}

GENERAL_DISCLAIMER = (
    "This application is intended only for educational and informational purposes "
    "and is NOT a substitute for professional medical advice, diagnosis, or treatment."
)


class RecommendationEngine:
    def generate(self, parameter_name: str, flag: ParameterFlag) -> dict | None:
        """Return a single recommendation dict for one abnormal parameter, or None if normal."""
        template = _TEMPLATES.get(flag)
        if not template:
            return None
        return {
            "parameter_name": parameter_name,
            "message": template.format(name=parameter_name),
            "severity": _SEVERITY_MAP.get(flag, RecommendationSeverity.INFO).value,
        }

    def generate_all(self, flagged_parameters: List[tuple[str, ParameterFlag]]) -> List[dict]:
        recommendations = []
        for name, flag in flagged_parameters:
            rec = self.generate(name, flag)
            if rec:
                recommendations.append(rec)

        # Always append the general disclaimer as the final, lowest-severity item.
        recommendations.append(
            {"parameter_name": None, "message": GENERAL_DISCLAIMER, "severity": "info"}
        )
        return recommendations

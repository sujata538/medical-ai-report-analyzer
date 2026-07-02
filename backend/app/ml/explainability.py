"""
Explainability module.

Provides a "why did I get this health score" breakdown. When SHAP + a
fitted scikit-learn model are available (see `future ML architecture` in
README for the prediction-model roadmap), this can attribute score impact
via real Shapley values. Until a predictive model exists, it exposes the
same interface backed by the transparent rule-based breakdown from
`health_score.py`, so the API/frontend contract never has to change when
the ML backend is upgraded.

Requires (for full SHAP mode): `pip install shap scikit-learn`.
"""
from __future__ import annotations

import logging
from typing import List, Tuple

from app.core.config import settings
from app.ml.health_score import score_breakdown
from app.models.parameter import ParameterFlag

logger = logging.getLogger(__name__)


class Explainability:
    def __init__(self):
        self.shap_available = False
        if settings.ENABLE_TRANSFORMER_MODELS:
            try:
                import shap  # noqa: F401
                import sklearn  # noqa: F401

                self.shap_available = True
                logger.info("SHAP + scikit-learn available for explainability.")
            except ImportError:
                logger.info("SHAP not installed — using rule-based score breakdown instead.")

    def explain_health_score(self, parameter_flags: List[Tuple[str, ParameterFlag]]) -> List[dict]:
        """
        Returns a list of {parameter, flag, score_impact} contributions.
        Currently always uses the transparent rule-based breakdown, since a
        trained predictive model (a prerequisite for real SHAP values) is
        part of the forward-looking roadmap (see docs/ROADMAP.md).
        """
        return score_breakdown(parameter_flags)

    def confidence_note(self) -> str:
        if self.shap_available:
            return "Explanations are model-based (SHAP) once a predictive model is trained."
        return (
            "Explanations are currently rule-based and fully transparent: "
            "each abnormal parameter's contribution is a fixed, documented weight."
        )

"""
Semantic similarity module.

Uses Sentence Transformers to match a raw/OCR'd, possibly misspelled or
abbreviated, parameter name (e.g. "Hgb", "Hemog.") against our canonical
parameter list and reference range database via cosine similarity of
sentence embeddings — this is what lets the system correctly recognize
"Hgb" as "Hemoglobin" even though the regex extractor's vocabulary list
doesn't include every abbreviation.

Requires: `pip install sentence-transformers` (downloads the model from
the internet on first use — see README.md "Enabling full ML features").

Falls back to simple string similarity (difflib) when the transformer
model isn't available, so the app still runs, just less robustly.
"""
from __future__ import annotations

import difflib
import logging
from typing import List, Optional, Tuple

from app.core.config import settings
from app.ml.regex_extractor import KNOWN_PARAMETERS

logger = logging.getLogger(__name__)


class SemanticMatcher:
    def __init__(self):
        self._model = None
        self._canonical_embeddings = None
        self.is_available = False
        self._load_model()

    def _load_model(self) -> None:
        if not settings.ENABLE_TRANSFORMER_MODELS:
            logger.info("SemanticMatcher disabled via ENABLE_TRANSFORMER_MODELS=False.")
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
            self._canonical_embeddings = self._model.encode(KNOWN_PARAMETERS, normalize_embeddings=True)
            self.is_available = True
            logger.info(
                "Loaded sentence-transformer model '%s' for semantic matching.",
                settings.SENTENCE_TRANSFORMER_MODEL,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Could not load sentence-transformers model (%s). "
                "Falling back to difflib string similarity for parameter matching.", exc,
            )
            self._model = None
            self.is_available = False

    def match_parameter_name(self, candidate: str, threshold: float = 0.6) -> Optional[Tuple[str, float]]:
        """
        Return (canonical_name, score) for the closest known parameter to
        `candidate`, or None if nothing clears the threshold.
        """
        if self.is_available and self._model is not None:
            return self._match_with_embeddings(candidate, threshold)
        return self._match_with_difflib(candidate, threshold)

    def _match_with_embeddings(self, candidate: str, threshold: float) -> Optional[Tuple[str, float]]:
        import numpy as np

        candidate_embedding = self._model.encode([candidate], normalize_embeddings=True)[0]
        scores = self._canonical_embeddings @ candidate_embedding
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        if best_score >= threshold:
            return KNOWN_PARAMETERS[best_idx], best_score
        return None

    def _match_with_difflib(self, candidate: str, threshold: float) -> Optional[Tuple[str, float]]:
        matches = difflib.get_close_matches(candidate, KNOWN_PARAMETERS, n=1, cutoff=threshold)
        if matches:
            ratio = difflib.SequenceMatcher(None, candidate.lower(), matches[0].lower()).ratio()
            return matches[0], ratio
        return None

    def summarize_similarity(self, texts: List[str]) -> List[List[float]]:
        """Pairwise cosine similarity matrix between arbitrary texts (used for
        deduplicating near-identical extracted lines across report pages)."""
        if self.is_available and self._model is not None:
            embeddings = self._model.encode(texts, normalize_embeddings=True)
            return (embeddings @ embeddings.T).tolist()

        # Fallback: pairwise difflib ratios
        n = len(texts)
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                matrix[i][j] = difflib.SequenceMatcher(None, texts[i], texts[j]).ratio()
        return matrix

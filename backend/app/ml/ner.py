"""
Medical Named Entity Recognition module.

Uses spaCy (with a scispaCy or biomedical model if available, falling back
to the standard `en_core_web_sm` model) to recognize lab parameter names,
quantities, and units in free text where the regex extractor's fixed
vocabulary misses non-standard phrasing.

Requires: `pip install spacy` and `python -m spacy download en_core_web_sm`
(needs internet access — see README.md "Enabling full ML features").

Design note: this module is intentionally optional. `MedicalNER.is_available`
tells callers whether to use it; `ExtractionService` falls back to
regex-only extraction when it's not.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class NEREntity:
    text: str
    label: str
    start: int
    end: int


class MedicalNER:
    """Thin wrapper around a spaCy pipeline for medical entity extraction."""

    def __init__(self):
        self._nlp = None
        self.is_available = False
        self._load_model()

    def _load_model(self) -> None:
        if not settings.ENABLE_TRANSFORMER_MODELS:
            logger.info("MedicalNER disabled via ENABLE_TRANSFORMER_MODELS=False.")
            return
        try:
            import spacy

            self._nlp = spacy.load(settings.SPACY_MODEL)
            self.is_available = True
            logger.info("Loaded spaCy model '%s' for medical NER.", settings.SPACY_MODEL)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Could not load spaCy model '%s' (%s). "
                "Run: python -m spacy download %s. Falling back to regex-only extraction.",
                settings.SPACY_MODEL, exc, settings.SPACY_MODEL,
            )
            self._nlp = None
            self.is_available = False

    def extract_entities(self, text: str) -> List[NEREntity]:
        """Return QUANTITY / measurement-like entities found via spaCy's NER."""
        if not self.is_available or self._nlp is None:
            return []

        doc = self._nlp(text)
        entities: List[NEREntity] = []
        for ent in doc.ents:
            if ent.label_ in {"QUANTITY", "CARDINAL", "PERCENT"}:
                entities.append(
                    NEREntity(text=ent.text, label=ent.label_, start=ent.start_char, end=ent.end_char)
                )
        return entities

    def extract_candidate_parameter_lines(self, text: str) -> List[str]:
        """
        Use noun-chunk analysis to surface lines that *look* like lab
        parameters but weren't caught by the fixed-vocabulary regex —
        useful as a "did we miss anything?" secondary pass.
        """
        if not self.is_available or self._nlp is None:
            return []

        candidates: List[str] = []
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) > 120:
                continue
            doc = self._nlp(line)
            has_number = any(tok.like_num for tok in doc)
            has_noun = any(tok.pos_ in ("NOUN", "PROPN") for tok in doc)
            if has_number and has_noun:
                candidates.append(line)
        return candidates

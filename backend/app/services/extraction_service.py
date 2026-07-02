"""
Extraction service.

Orchestrates the full text->structured-parameters pipeline:
    1. RegexExtractor pulls out (name, value, unit) tuples (always runs).
    2. MedicalNER surfaces additional candidate lines regex may have missed
       (only if transformer models are enabled).
    3. SemanticMatcher normalizes any non-canonical parameter names to a
       known canonical name so reference-range lookups succeed.

Returns confidence-scored `ExtractedValue` objects ready to be persisted.
"""
from __future__ import annotations

import logging
from typing import List

from app.ml.ner import MedicalNER
from app.ml.regex_extractor import ExtractedValue, RegexExtractor
from app.ml.semantic import SemanticMatcher

logger = logging.getLogger(__name__)


class ExtractionService:
    def __init__(self):
        self.regex_extractor = RegexExtractor()
        self.ner = MedicalNER()
        self.semantic_matcher = SemanticMatcher()

    def extract_parameters(self, raw_text: str) -> List[ExtractedValue]:
        results = self.regex_extractor.extract(raw_text)
        found_names = {r.name.lower() for r in results}

        if self.ner.is_available:
            candidate_lines = self.ner.extract_candidate_parameter_lines(raw_text)
            for line in candidate_lines:
                self._try_semantic_recovery(line, found_names, results)

        logger.info("Extraction pipeline found %d parameters.", len(results))
        return results

    def _try_semantic_recovery(
        self, line: str, found_names: set[str], results: List[ExtractedValue]
    ) -> None:
        """
        Attempt to recover a parameter from a candidate line the regex
        extractor skipped, by matching its leading words against the
        canonical parameter vocabulary via semantic similarity.
        """
        import re

        from app.ml.regex_extractor import NUMBER_PATTERN

        number_match = re.search(NUMBER_PATTERN, line)
        if not number_match:
            return

        candidate_name = line[: number_match.start()].strip(" :-\t")
        if not candidate_name or len(candidate_name) > 60:
            return

        match = self.semantic_matcher.match_parameter_name(candidate_name)
        if not match:
            return

        canonical_name, score = match
        if canonical_name.lower() in found_names:
            return

        results.append(
            ExtractedValue(
                name=canonical_name,
                raw_text=line,
                value=float(number_match.group()),
                unit=None,
                confidence=round(0.4 * score, 2),  # lower confidence: recovered, not directly matched
            )
        )
        found_names.add(canonical_name.lower())

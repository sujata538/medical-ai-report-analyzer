"""
Regex-based lab parameter extractor.

This is the reliable baseline extraction layer: it works with zero ML
dependencies and handles the vast majority of standard lab report layouts
of the form:

    Hemoglobin        13.5 g/dL      (13.0 - 17.0)
    WBC Count: 7200 /uL
    Glucose (Fasting) - 95 mg/dL

The `MedicalNER` module (app/ml/ner.py) can be layered on top for reports
with less predictable formatting, but this extractor is designed to
require no external models at all.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

# Common lab parameter names we specifically look for, mapped to
# normalized canonical names. This list is intentionally extensible.
KNOWN_PARAMETERS = [
    "Hemoglobin", "Hematocrit", "WBC Count", "White Blood Cell Count", "RBC Count",
    "Red Blood Cell Count", "Platelet Count", "MCV", "MCH", "MCHC",
    "Glucose", "Fasting Glucose", "HbA1c", "Total Cholesterol", "LDL Cholesterol",
    "HDL Cholesterol", "Triglycerides", "Creatinine", "Blood Urea Nitrogen", "BUN",
    "Sodium", "Potassium", "Chloride", "Calcium", "Albumin", "Total Protein",
    "ALT", "AST", "Alkaline Phosphatase", "Bilirubin", "TSH", "T3", "T4",
    "Vitamin D", "Vitamin B12", "Ferritin", "Iron", "Uric Acid", "CRP", "ESR",
]

# Units commonly seen in lab reports
UNIT_PATTERN = r"(mg/dL|g/dL|/uL|/µL|mmol/L|µmol/L|umol/L|IU/L|U/L|ng/mL|pg/mL|%|mIU/L|mEq/L|fL|pg)"

NUMBER_PATTERN = r"[-+]?\d{1,6}(?:\.\d{1,4})?"


@dataclass
class ExtractedValue:
    name: str
    raw_text: str
    value: float
    unit: Optional[str]
    confidence: float


def _build_parameter_pattern() -> re.Pattern:
    """
    Builds a single regex that matches: `<parameter name> ... <number> <unit>?`
    across a line, tolerant of colons, dashes, and extra whitespace.
    """
    names_alternation = "|".join(re.escape(name) for name in KNOWN_PARAMETERS)
    pattern = (
        rf"(?P<name>{names_alternation})"
        rf"[\s:.\-]*"
        rf"(?P<value>{NUMBER_PATTERN})"
        rf"\s*(?P<unit>{UNIT_PATTERN})?"
    )
    return re.compile(pattern, re.IGNORECASE)


_PARAMETER_REGEX = _build_parameter_pattern()

# Generic fallback pattern for "Some Parameter Name: 12.3 unit" where the
# name isn't in our known list — lower confidence, still useful.
_GENERIC_REGEX = re.compile(
    rf"(?P<name>[A-Za-z][A-Za-z0-9 /()\-]{{2,40}}?)\s*[:\-]\s*"
    rf"(?P<value>{NUMBER_PATTERN})\s*(?P<unit>{UNIT_PATTERN})?",
    re.IGNORECASE,
)


class RegexExtractor:
    """Extracts structured (name, value, unit) tuples from raw OCR/PDF text."""

    def extract(self, text: str) -> List[ExtractedValue]:
        results: List[ExtractedValue] = []
        seen_names: set[str] = set()

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            match = _PARAMETER_REGEX.search(line)
            if match:
                name = self._canonicalize(match.group("name"))
                if name.lower() in seen_names:
                    continue
                results.append(
                    ExtractedValue(
                        name=name,
                        raw_text=line,
                        value=float(match.group("value")),
                        unit=match.group("unit"),
                        confidence=0.9,  # matched a known parameter name
                    )
                )
                seen_names.add(name.lower())
                continue

            # Fallback: generic "Name: number unit" pattern, lower confidence
            generic_match = _GENERIC_REGEX.search(line)
            if generic_match:
                name = self._normalize_name(generic_match.group("name"))
                if len(name) < 3 or name.lower() in seen_names:
                    continue
                results.append(
                    ExtractedValue(
                        name=name,
                        raw_text=line,
                        value=float(generic_match.group("value")),
                        unit=generic_match.group("unit"),
                        confidence=0.5,  # unverified parameter name
                    )
                )
                seen_names.add(name.lower())

        return results

    @staticmethod
    def _canonicalize(raw_name: str) -> str:
        """Map a regex-matched name back to its canonical casing in KNOWN_PARAMETERS."""
        cleaned = raw_name.strip().strip(":-").strip()
        for canonical in KNOWN_PARAMETERS:
            if canonical.lower() == cleaned.lower():
                return canonical
        return RegexExtractor._normalize_name(cleaned)

    @staticmethod
    def _normalize_name(raw_name: str) -> str:
        name = raw_name.strip().strip(":-").strip()
        # Title-case unless it looks like an acronym (e.g. "WBC", "TSH")
        if name.isupper() and len(name) <= 6:
            return name
        return name.title() if not name.isupper() else name

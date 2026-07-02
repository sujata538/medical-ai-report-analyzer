"""Unit tests for the regex-based parameter extractor."""
from app.ml.regex_extractor import RegexExtractor


SAMPLE_REPORT_TEXT = """
COMPLETE BLOOD COUNT
Hemoglobin: 12.1 g/dL
WBC Count: 15200 /uL
Platelet Count 210000 /uL
Glucose - 105 mg/dL
Random line with no parameter
"""


def test_extracts_known_parameters():
    extractor = RegexExtractor()
    results = extractor.extract(SAMPLE_REPORT_TEXT)
    names = {r.name for r in results}

    assert "Hemoglobin" in names
    assert "Glucose" in names
    hemoglobin = next(r for r in results if r.name == "Hemoglobin")
    assert hemoglobin.value == 12.1
    assert hemoglobin.unit == "g/dL"


def test_ignores_lines_without_parameters():
    extractor = RegexExtractor()
    results = extractor.extract("This is just some narrative text with no lab values.")
    assert results == []


def test_deduplicates_repeated_parameters():
    text = "Glucose: 90 mg/dL\nGlucose: 95 mg/dL"
    extractor = RegexExtractor()
    results = extractor.extract(text)
    glucose_matches = [r for r in results if r.name == "Glucose"]
    assert len(glucose_matches) == 1

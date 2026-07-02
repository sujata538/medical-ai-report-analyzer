"""Unit tests for the health scoring algorithm."""
from app.ml.health_score import categorize_risk, compute_health_score
from app.models.parameter import ParameterFlag


def test_perfect_score_when_all_normal():
    flags = [("Hemoglobin", ParameterFlag.NORMAL), ("Glucose", ParameterFlag.NORMAL)]
    assert compute_health_score(flags) == 100.0


def test_score_deducted_for_abnormal_parameters():
    flags = [("Hemoglobin", ParameterFlag.HIGH)]
    score = compute_health_score(flags)
    assert score < 100.0


def test_critical_flags_deduct_more_than_mild_flags():
    mild = compute_health_score([("Hemoglobin", ParameterFlag.HIGH)])
    critical = compute_health_score([("Hemoglobin", ParameterFlag.CRITICAL_HIGH)])
    assert critical < mild


def test_score_never_goes_below_zero():
    flags = [("Hemoglobin", ParameterFlag.CRITICAL_HIGH)] * 20
    assert compute_health_score(flags) == 0.0


def test_risk_categorization_boundaries():
    assert categorize_risk(95) == "excellent"
    assert categorize_risk(80) == "good"
    assert categorize_risk(60) == "moderate"
    assert categorize_risk(40) == "elevated"
    assert categorize_risk(10) == "high"

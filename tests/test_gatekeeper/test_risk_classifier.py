"""
Tests for Developer 1's risk classification service.
"""

import pytest
from services.gatekeeper.risk_classifier import (
    classify_risk,
    calculate_risk_score,
    calculate_confidence,
    map_risk_to_severity,
)
from shared.schemas.analysis_result import DetectedElement
from shared.schemas.policy_context import PolicyThresholds
from shared.enums import RiskCategory, SeverityColor, ConfidenceLevel


class TestClassifyRisk:
    """Tests for risk category classification."""

    def test_returns_unique_categories(self):
        elements = [
            DetectedElement(text="test", category=RiskCategory.PII, start_index=0, end_index=4, confidence=0.9),
            DetectedElement(text="test2", category=RiskCategory.PII, start_index=5, end_index=10, confidence=0.8),
            DetectedElement(text="revenue", category=RiskCategory.FINANCIAL, start_index=11, end_index=18, confidence=0.7),
        ]
        categories = classify_risk(elements)
        assert RiskCategory.PII in categories
        assert RiskCategory.FINANCIAL in categories
        assert len(categories) == 2

    def test_empty_elements_returns_empty(self):
        categories = classify_risk([])
        assert categories == []


class TestCalculateRiskScore:
    """Tests for risk score calculation."""

    def test_credentials_score_high(self):
        score = calculate_risk_score(
            detected_categories=[RiskCategory.CREDENTIALS],
            data_volume=1,
            user_role="analyst",
            policy_mode="BALANCED",
        )
        assert score > 30

    def test_empty_categories_score_zero(self):
        score = calculate_risk_score(
            detected_categories=[],
            data_volume=0,
            user_role="analyst",
            policy_mode="BALANCED",
        )
        assert score == 0

    def test_strict_mode_increases_score(self):
        score_balanced = calculate_risk_score(
            detected_categories=[RiskCategory.PII],
            data_volume=1,
            user_role="analyst",
            policy_mode="BALANCED",
        )
        score_strict = calculate_risk_score(
            detected_categories=[RiskCategory.PII],
            data_volume=1,
            user_role="analyst",
            policy_mode="STRICT",
        )
        assert score_strict > score_balanced


class TestMapRiskToSeverity:
    """Tests for severity color mapping."""

    def test_low_score_is_yellow(self):
        thresholds = PolicyThresholds()
        assert map_risk_to_severity(10.0, thresholds) == SeverityColor.YELLOW

    def test_medium_score_is_orange(self):
        thresholds = PolicyThresholds()
        assert map_risk_to_severity(50.0, thresholds) == SeverityColor.ORANGE

    def test_high_score_is_red(self):
        thresholds = PolicyThresholds()
        assert map_risk_to_severity(80.0, thresholds) == SeverityColor.RED


class TestCalculateConfidence:
    """Tests for confidence level calculation."""

    def test_high_confidence_elements(self):
        elements = [
            DetectedElement(text="test", category=RiskCategory.CREDENTIALS, start_index=0, end_index=4, confidence=0.95),
        ]
        assert calculate_confidence(elements) == ConfidenceLevel.HIGH

    def test_empty_elements_is_low(self):
        assert calculate_confidence([]) == ConfidenceLevel.LOW

"""
Tests for Developer 1's safer prompt rewrite engine.
"""

import pytest
from services.gatekeeper.rewrite_engine import (
    generate_safer_rewrite,
    replace_credentials,
    generate_rewrite_explanation,
)
from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory


class TestGenerateSaferRewrite:
    """Tests for the master rewrite function."""

    def test_replaces_credential_in_prompt(self):
        elements = [
            DetectedElement(
                text="sk_live_abc123def456",
                category=RiskCategory.CREDENTIALS,
                start_index=14,
                end_index=34,
                confidence=0.95,
            ),
        ]
        result = generate_safer_rewrite(
            raw_prompt="My API key is sk_live_abc123def456 and I need help.",
            flagged_elements=elements,
            risk_categories=[RiskCategory.CREDENTIALS],
        )
        assert "[REDACTED_CREDENTIAL]" in result["safer_prompt"]
        assert "sk_live_abc123def456" not in result["safer_prompt"]

    def test_returns_explanation(self):
        elements = [
            DetectedElement(
                text="revenue",
                category=RiskCategory.FINANCIAL,
                start_index=4,
                end_index=11,
                confidence=0.7,
            ),
        ]
        result = generate_safer_rewrite(
            raw_prompt="Our revenue is growing.",
            flagged_elements=elements,
            risk_categories=[RiskCategory.FINANCIAL],
        )
        assert len(result["explanation"]) > 0

    def test_no_elements_returns_original(self):
        result = generate_safer_rewrite(
            raw_prompt="What is the weather?",
            flagged_elements=[],
            risk_categories=[],
        )
        assert result["safer_prompt"] == "What is the weather?"


class TestRewriteExplanation:
    """Tests for rewrite explanation generation."""

    def test_no_transformations_returns_message(self):
        explanation = generate_rewrite_explanation("original", "original", [])
        assert "No changes" in explanation[0]

    def test_transformations_listed(self):
        transformations = ["Replaced 'test' with '[REDACTED]'"]
        explanation = generate_rewrite_explanation("test", "[REDACTED]", transformations)
        assert len(explanation) == 1

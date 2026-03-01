"""
Tests for Developer 3's alerting service.
"""

import pytest
from services.watchtower.alerting_service import (
    create_incident_report,
    generate_privacy_safe_manager_alert,
    check_escalation_rules,
)


class TestCreateIncidentReport:
    """Tests for incident report creation."""

    def test_returns_valid_report(self):
        report = create_incident_report(
            user_id="EMP001",
            prompt="Test prompt with sensitive data",
            risk_category="PII",
            action_taken="REWRITTEN",
            policy_version="1.0.0",
            confidence_score="HIGH",
            timestamp="2026-01-15T10:30:00Z",
            severity_color="ORANGE",
        )
        assert "incident_id" in report
        assert report["user_id"] == "EMP001"
        assert report["severity_color"] == "ORANGE"

    def test_does_not_include_raw_prompt(self):
        """Incident report should store prompt length, not the raw prompt itself in alerts."""
        report = create_incident_report(
            user_id="EMP001",
            prompt="Super secret prompt",
            risk_category="CREDENTIALS",
            action_taken="BLOCKED",
            policy_version="1.0.0",
            confidence_score="HIGH",
            timestamp="2026-01-15T10:30:00Z",
            severity_color="RED",
        )
        assert "Super secret prompt" not in str(report.get("prompt_length"))


class TestPrivacySafeAlert:
    """Tests for privacy-safe manager alerts."""

    def test_strips_sensitive_info(self):
        report = {
            "severity_color": "ORANGE",
            "risk_category": "PII",
            "action_taken": "REWRITTEN",
            "raw_prompt": "This should not appear",
        }
        alert = generate_privacy_safe_manager_alert(report)
        assert "ORANGE" in alert
        assert "PII" in alert
        assert "This should not appear" not in alert


class TestEscalationRules:
    """Tests for escalation rule lookup."""

    def test_returns_escalation_path(self):
        rules = check_escalation_rules("DEPT_MKT", "PII_LEAK")
        assert "escalation_path" in rules

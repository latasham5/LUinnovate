"""
Tests for Developer 3's logging service.
"""

import pytest
from services.watchtower.logging_service import log_prompt_event, generate_audit_summary
from shared.schemas.flag_record import FlagRecord
from shared.enums import RiskCategory, SeverityColor, ActionType, PolicyMode, DeploymentMode, ConfidenceLevel


class TestLogPromptEvent:
    """Tests for prompt event logging."""

    @pytest.mark.asyncio
    async def test_returns_incident_id(self):
        record = FlagRecord(
            user_id="EMP001",
            department="Marketing",
            department_id="DEPT_MKT",
            raw_prompt="Test prompt",
            risk_category=RiskCategory.GENERAL,
            risk_score=0.0,
            severity_color=SeverityColor.YELLOW,
            confidence_score=ConfidenceLevel.LOW,
            action_taken=ActionType.ALLOWED,
            policy_version="1.0.0",
            policy_mode=PolicyMode.BALANCED,
            deployment_mode=DeploymentMode.SHADOW,
        )
        incident_id = await log_prompt_event(record)
        assert incident_id is not None


class TestAuditSummary:
    """Tests for audit summary generation."""

    @pytest.mark.asyncio
    async def test_returns_summary_dict(self):
        summary = await generate_audit_summary()
        assert "total_prompts" in summary
        assert "flagged_prompts" in summary

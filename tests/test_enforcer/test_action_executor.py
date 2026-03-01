"""
Tests for Developer 2's action execution service.
"""

import pytest
from services.enforcer.action_executor import block_prompt, scan_gpt_response
from shared.enums import ActionType


class TestBlockPrompt:
    """Tests for prompt blocking."""

    def test_returns_blocked_action(self):
        result = block_prompt(
            user_id="EMP001",
            raw_prompt="Test prompt",
            reason="Credentials detected",
            policy_version="1.0.0",
        )
        assert result["action"] == ActionType.BLOCKED.value
        assert result["response_content"] is None
        assert "blocked" in result["warning_message"].lower()


class TestScanGPTResponse:
    """Tests for GPT response scanning."""

    def test_clean_response_passes(self):
        result = scan_gpt_response("This is a clean response about marketing strategies.")
        assert result["clean"] is True

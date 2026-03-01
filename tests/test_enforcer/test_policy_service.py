"""
Tests for Developer 2's policy management service.
"""

import pytest
from services.enforcer.policy_service import (
    get_active_policies,
    get_policy_version,
    get_policy_thresholds_by_mode,
    build_policy_context,
)
from shared.schemas.policy_context import UserProfile


class TestGetActivePolicies:
    """Tests for active policy retrieval."""

    def test_returns_policy_list(self):
        policies = get_active_policies()
        assert isinstance(policies, list)

    def test_policies_have_required_fields(self):
        policies = get_active_policies()
        if policies:
            policy = policies[0]
            assert hasattr(policy, "rule_id")
            assert hasattr(policy, "category")
            assert hasattr(policy, "action")


class TestPolicyThresholds:
    """Tests for policy threshold calculation."""

    def test_balanced_mode_defaults(self):
        thresholds = get_policy_thresholds_by_mode("BALANCED")
        assert thresholds.yellow_min == 1.0
        assert thresholds.red_min == 70.0

    def test_strict_mode_lower_thresholds(self):
        strict = get_policy_thresholds_by_mode("STRICT")
        balanced = get_policy_thresholds_by_mode("BALANCED")
        assert strict.red_min < balanced.red_min


class TestBuildPolicyContext:
    """Tests for building the complete policy context."""

    def test_builds_valid_context(self):
        user = UserProfile(
            employee_id="EMP001",
            name="Test User",
            email="test@coca-cola.com",
            role="analyst",
            department="Marketing",
            department_id="DEPT_MKT",
            clearance_level="standard",
        )
        context = build_policy_context(user)
        assert context.user_profile.employee_id == "EMP001"
        assert context.policy_version is not None
        assert context.deployment_mode is not None

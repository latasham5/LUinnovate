"""
Tests for Developer 2's authentication service.
"""

import pytest
from services.enforcer.auth_service import (
    validate_sso_token,
    get_user_profile,
    generate_session_token,
    revoke_session,
    get_deployment_mode,
)
from shared.exceptions import AuthenticationError


class TestValidateSSOToken:
    """Tests for SSO token validation."""

    def test_valid_token_returns_employee_id(self):
        result = validate_sso_token("valid_test_token")
        assert result["valid"] is True
        assert "employee_id" in result

    def test_empty_token_raises_error(self):
        with pytest.raises(AuthenticationError):
            validate_sso_token("")


class TestGetUserProfile:
    """Tests for user profile retrieval."""

    def test_returns_mock_user(self):
        profile = get_user_profile("EMP001")
        assert profile.employee_id == "EMP001"
        assert profile.department is not None

    def test_unknown_user_returns_default(self):
        profile = get_user_profile("UNKNOWN_USER")
        assert profile.employee_id == "UNKNOWN_USER"
        assert profile.role == "analyst"


class TestSessionManagement:
    """Tests for session token management."""

    def test_generate_and_revoke_session(self):
        token = generate_session_token("EMP001")
        assert token is not None
        assert len(token) > 0

        revoked = revoke_session(token)
        assert revoked is True

    def test_revoke_nonexistent_session(self):
        revoked = revoke_session("nonexistent_token")
        assert revoked is False


class TestDeploymentMode:
    """Tests for deployment mode retrieval."""

    def test_returns_valid_mode(self):
        mode = get_deployment_mode()
        assert mode in ("SHADOW", "FULL_ENFORCEMENT")

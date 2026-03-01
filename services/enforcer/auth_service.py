"""
Authentication & Authorization Service.

validateSSOToken, getUserProfile, getManagerByEmployee,
getDepartmentSecurityTeam, checkAccessPermissions,
generateSessionToken, revokeSession, getDeploymentMode.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from shared.schemas.policy_context import UserProfile
from shared.exceptions import AuthenticationError, AuthorizationError
from config.settings import settings
from config.constants import SESSION_TIMEOUT_MINUTES

# Path to mock users data
MOCK_USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_users", "users.json")

# In-memory session store (replace with Redis/DB in production)
_active_sessions: dict[str, dict] = {}


def _load_mock_users() -> list[dict]:
    """Load mock user profiles from JSON file."""
    try:
        with open(MOCK_USERS_FILE, "r") as f:
            return json.load(f).get("users", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def validate_sso_token(sso_token: str) -> dict:
    """
    Verify the SSO token against Coca-Cola's identity provider.
    In development, accepts any non-empty token and returns a mock user.
    """
    if not sso_token:
        raise AuthenticationError("Empty SSO token")

    if settings.APP_ENV == "development":
        # In dev mode, extract employee_id from token or use default
        return {"valid": True, "employee_id": "EMP001"}

    # TODO: Integrate with Coca-Cola's real identity provider
    raise AuthenticationError("SSO validation not implemented for production")


def get_user_profile(employee_id: str) -> UserProfile:
    """
    Query directory for name, role, department, clearance level.
    In development, returns mock user data.
    """
    mock_users = _load_mock_users()

    for user in mock_users:
        if user["employee_id"] == employee_id:
            return UserProfile(**user)

    # Default dev user if not found
    return UserProfile(
        employee_id=employee_id,
        name="Dev User",
        email="dev@coca-cola.com",
        role="analyst",
        department="Marketing",
        department_id="DEPT_MKT",
        clearance_level="standard",
        manager_id="MGR001",
    )


def get_manager_by_employee(employee_id: str) -> Optional[str]:
    """Org chart lookup for escalation routing."""
    profile = get_user_profile(employee_id)
    return profile.manager_id


def get_department_security_team(department_id: str) -> list[str]:
    """Retrieve assigned cybersecurity contacts for a department."""
    # TODO: Query org chart / directory
    return ["SEC001", "SEC002"]


def check_access_permissions(employee_id: str, resource_type: str) -> bool:
    """Role-based access evaluation."""
    profile = get_user_profile(employee_id)

    # Admin has access to everything
    if profile.role in ("admin", "security_admin"):
        return True

    # Managers can access their department's data
    if profile.role == "manager" and resource_type in ("department_audit", "department_scorecard"):
        return True

    # Standard users can only access their own data
    if resource_type in ("own_audit", "own_training"):
        return True

    return False


def generate_session_token(user_id: str) -> str:
    """Create an internal session token."""
    token = str(uuid.uuid4())
    _active_sessions[token] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES),
    }
    return token


def revoke_session(session_id: str) -> bool:
    """Kill a session on timeout or security event."""
    if session_id in _active_sessions:
        del _active_sessions[session_id]
        return True
    return False


def get_deployment_mode() -> str:
    """Return current deployment mode: SHADOW or FULL_ENFORCEMENT."""
    return settings.DEPLOYMENT_MODE

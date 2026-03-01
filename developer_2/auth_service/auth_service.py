"""
Authentication & Authorization Service
Developer 2 - The Enforcer
"""
import uuid
import json
import os

MOCK_USERS_PATH = os.path.join(os.path.dirname(__file__), "mock_users.json")

# Default mock data if file doesn't exist
DEFAULT_USERS = {
    "EMP001": {
        "name": "Alice Johnson",
        "role": "analyst",
        "department": "marketing",
        "clearance": "standard",
        "manager": "EMP010",
        "security_team": "SEC-MKT-01"
    },
    "EMP002": {
        "name": "Bob Smith",
        "role": "engineer",
        "department": "engineering",
        "clearance": "elevated",
        "manager": "EMP011",
        "security_team": "SEC-ENG-01"
    },
    "EMP010": {
        "name": "Carol Davis",
        "role": "manager",
        "department": "marketing",
        "clearance": "elevated",
        "manager": "EMP100",
        "security_team": "SEC-MKT-01"
    }
}

DEPLOYMENT_MODE = "SHADOW"  # SHADOW or FULL_ENFORCEMENT

_sessions = {}


def _load_users():
    if os.path.exists(MOCK_USERS_PATH):
        with open(MOCK_USERS_PATH, "r") as f:
            return json.load(f)
    return DEFAULT_USERS


def validate_sso_token(sso_token: str) -> dict:
    """Verify SSO token against mock identity provider."""
    # Mock: token format is "SSO-<employeeId>"
    if not sso_token or not sso_token.startswith("SSO-"):
        return {"valid": False, "error": "Invalid SSO token format"}
    emp_id = sso_token.replace("SSO-", "")
    users = _load_users()
    if emp_id in users:
        return {"valid": True, "employee_id": emp_id}
    return {"valid": False, "error": "Employee not found"}


def get_user_profile(employee_id: str) -> dict | None:
    """Query directory for user profile."""
    users = _load_users()
    profile = users.get(employee_id)
    if profile:
        return {"employee_id": employee_id, **profile}
    return None


def get_manager_by_employee(employee_id: str) -> str | None:
    """Org chart lookup for escalation routing."""
    profile = get_user_profile(employee_id)
    return profile.get("manager") if profile else None


def get_department_security_team(department_id: str) -> str | None:
    """Retrieve assigned cybersecurity contacts for a department."""
    users = _load_users()
    for u in users.values():
        if u["department"] == department_id:
            return u.get("security_team")
    return None


def check_access_permissions(employee_id: str, resource_type: str) -> bool:
    """Role-based access evaluation."""
    profile = get_user_profile(employee_id)
    if not profile:
        return False
    permission_map = {
        "standard": ["read", "prompt"],
        "elevated": ["read", "prompt", "admin_view"],
        "admin": ["read", "prompt", "admin_view", "admin_write"]
    }
    clearance = profile.get("clearance", "standard")
    allowed = permission_map.get(clearance, [])
    return resource_type in allowed


def generate_session_token(user_id: str) -> str:
    """Create internal session token."""
    token = str(uuid.uuid4())
    _sessions[token] = {"user_id": user_id, "active": True}
    return token


def revoke_session(session_id: str) -> bool:
    """Kill session on timeout or security event."""
    if session_id in _sessions:
        _sessions[session_id]["active"] = False
        return True
    return False


def get_deployment_mode() -> str:
    """Return current deployment mode: SHADOW or FULL_ENFORCEMENT."""
    return DEPLOYMENT_MODE


if __name__ == "__main__":
    # Quick smoke test
    result = validate_sso_token("SSO-EMP001")
    print("SSO Validation:", result)
    print("Profile:", get_user_profile("EMP001"))
    print("Manager:", get_manager_by_employee("EMP001"))
    print("Access:", check_access_permissions("EMP001", "prompt"))
    tok = generate_session_token("EMP001")
    print("Session Token:", tok)
    print("Revoke:", revoke_session(tok))
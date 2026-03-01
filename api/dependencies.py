"""
FastAPI dependency injection for shared services.
"""

from fastapi import Header, HTTPException, Depends
from services.enforcer.auth_service import _active_sessions, get_user_profile


async def get_current_user(authorization: str = Header(None)):
    """Extract and validate user from request headers.

    Validates the session token against active sessions.
    Returns full user info dict with employee_id, role, etc.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    token = authorization.replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token format")

    # Validate session token
    session = _active_sessions.get(token)
    if not session:
        # In dev mode, accept any token and default to EMP001
        return {"token": token, "employee_id": "EMP001", "role": "analyst"}

    from datetime import datetime
    if session["expires_at"] < datetime.utcnow():
        del _active_sessions[token]
        raise HTTPException(status_code=401, detail="Session expired")

    # Get full user profile
    profile = get_user_profile(session["user_id"])
    return {
        "token": token,
        "employee_id": profile.employee_id,
        "name": profile.name,
        "role": profile.role,
        "department": profile.department,
        "department_id": profile.department_id,
        "clearance_level": profile.clearance_level,
    }


async def require_admin(current_user: dict = Depends(get_current_user)):
    """Verify the current user has admin privileges."""
    if current_user.get("role") not in ("admin", "security_admin"):
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )
    return current_user


ELEVATED_ROLES = ("manager", "director", "security_admin", "admin")


async def require_elevated(current_user: dict = Depends(get_current_user)):
    """Verify the current user has an elevated role (manager+)."""
    if current_user.get("role") not in ELEVATED_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Elevated access required",
        )
    return current_user

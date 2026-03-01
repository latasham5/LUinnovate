"""
Authentication routes — login, session management, user profile.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class LoginRequest(BaseModel):
    """SSO login request."""
    sso_token: str


class LoginResponse(BaseModel):
    """Session token response."""
    session_token: str
    user_id: str
    name: str
    role: str
    department: str
    deployment_mode: str


class UserProfileResponse(BaseModel):
    """User profile from directory."""
    employee_id: str
    name: str
    email: str
    role: str
    department: str
    department_id: str
    clearance_level: str
    manager_id: Optional[str] = None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Validate SSO token and create internal session."""
    # TODO: enforcer.auth_service.validateSSOToken + generateSessionToken
    return LoginResponse(
        session_token="placeholder_session_token",
        user_id="EMP001",
        name="Dev User",
        role="analyst",
        department="Marketing",
        deployment_mode="SHADOW",
    )


@router.get("/profile/{employee_id}", response_model=UserProfileResponse)
async def get_profile(employee_id: str):
    """Get employee profile from directory."""
    # TODO: enforcer.auth_service.getUserProfile
    return UserProfileResponse(
        employee_id=employee_id,
        name="Dev User",
        email="dev@coca-cola.com",
        role="analyst",
        department="Marketing",
        department_id="DEPT_MKT",
        clearance_level="standard",
        manager_id="MGR001",
    )


@router.post("/logout")
async def logout():
    """Revoke current session."""
    # TODO: enforcer.auth_service.revokeSession
    return {"message": "Session revoked"}

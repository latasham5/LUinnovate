"""
Authentication routes — login, session management, user profile.

Mock auth: users log in with employee_id (e.g., "EMP001").
The sso_token field accepts employee_id directly in dev mode.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from services.enforcer.auth_service import (
    validate_sso_token,
    get_user_profile,
    generate_session_token,
    revoke_session,
    get_deployment_mode,
)

router = APIRouter()


class LoginRequest(BaseModel):
    """SSO login request. In dev mode, pass employee_id as sso_token."""
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
    # In dev mode, sso_token is the employee_id directly
    validation = validate_sso_token(request.sso_token)
    employee_id = validation["employee_id"]

    # Get full user profile
    profile = get_user_profile(employee_id)

    # Generate session token
    session_token = generate_session_token(employee_id)

    return LoginResponse(
        session_token=session_token,
        user_id=profile.employee_id,
        name=profile.name,
        role=profile.role,
        department=profile.department,
        deployment_mode=get_deployment_mode(),
    )


@router.get("/profile/{employee_id}", response_model=UserProfileResponse)
async def get_profile(employee_id: str):
    """Get employee profile from directory."""
    profile = get_user_profile(employee_id)
    return UserProfileResponse(
        employee_id=profile.employee_id,
        name=profile.name,
        email=profile.email,
        role=profile.role,
        department=profile.department,
        department_id=profile.department_id,
        clearance_level=profile.clearance_level,
        manager_id=profile.manager_id,
    )


@router.post("/logout")
async def logout(request: Request):
    """Revoke current session."""
    token = getattr(request.state, "token", None)
    if token:
        revoke_session(token)
    return {"message": "Session revoked"}

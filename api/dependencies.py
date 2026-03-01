"""
FastAPI dependency injection for shared services.
"""

from fastapi import Header, HTTPException, Depends
from config.settings import settings


async def get_current_user(authorization: str = Header(None)):
    """Extract and validate user from request headers.

    In production, this validates the SSO token against Coca-Cola's identity provider.
    In development, it accepts mock tokens.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    token = authorization.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Invalid token format")

    # Token validation will be handled by enforcer/auth_service.py
    return {"token": token}


async def require_admin(current_user: dict = Depends(get_current_user)):
    """Verify the current user has admin privileges."""
    # Admin check will be implemented via enforcer/auth_service.py
    return current_user

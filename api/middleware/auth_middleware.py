"""
Authentication middleware — validates SSO tokens on every request.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Routes that don't require authentication
PUBLIC_ROUTES = [
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
]


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate SSO tokens on protected routes."""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public routes
        if request.url.path in PUBLIC_ROUTES:
            return await call_next(request)

        # Skip auth for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header required", "code": "AUTH_ERROR"},
            )

        token = auth_header.replace("Bearer ", "")
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token format", "code": "AUTH_ERROR"},
            )

        # Store token in request state for downstream use
        request.state.token = token

        # Full token validation happens in the auth_service
        # Middleware just ensures the header exists
        response = await call_next(request)
        return response

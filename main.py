"""
Phantom App — Prompt Security Middleware for CokeGPT

Main entry point for the FastAPI application.
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import api_router
from api.middleware.auth_middleware import AuthMiddleware
from config.settings import settings

# Create FastAPI app
app = FastAPI(
    title="Phantom App",
    description="Prompt Security Middleware — intercepts, analyzes, and sanitizes prompts before they reach CokeGPT.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware
app.add_middleware(AuthMiddleware)

# Register all API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint — health check and app info."""
    return {
        "app": "Phantom App",
        "version": "1.0.0",
        "status": "running",
        "deployment_mode": settings.DEPLOYMENT_MODE,
        "policy_mode": settings.DEFAULT_POLICY_MODE,
        "environment": settings.APP_ENV,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )

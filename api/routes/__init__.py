from fastapi import APIRouter
from api.routes import prompt, auth, policy, admin, dashboard, training, audit

api_router = APIRouter()

api_router.include_router(prompt.router, prefix="/prompt", tags=["Prompt"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(policy.router, prefix="/policy", tags=["Policy"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(training.router, prefix="/training", tags=["Training"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])

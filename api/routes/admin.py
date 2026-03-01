"""
Admin routes — shadow mode management, deployment config.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from api.dependencies import require_admin
from config.settings import settings
from services.enforcer.shadow_mode_service import (
    get_deployment_mode as _get_deployment_mode,
    set_deployment_mode as _set_deployment_mode,
    get_shadow_mode_config as _get_shadow_mode_config,
    update_shadow_mode_config as _update_shadow_mode_config,
    generate_shadow_to_enforcement_readiness_report as _generate_readiness_report,
    compare_shadow_vs_enforcement as _compare_shadow_vs_enforcement,
)

router = APIRouter()


class DeploymentModeRequest(BaseModel):
    """Request to switch deployment mode."""
    admin_id: str
    mode: str  # SHADOW or FULL_ENFORCEMENT
    effective_date: str


class ShadowModeConfigRequest(BaseModel):
    """Request to update shadow mode configuration."""
    admin_id: str
    config: dict


@router.get("/deployment-mode")
async def get_deployment_mode():
    """Return current deployment mode (SHADOW or FULL_ENFORCEMENT)."""
    mode = _get_deployment_mode()
    return {"mode": mode}


@router.put("/deployment-mode")
async def set_deployment_mode(request: DeploymentModeRequest, admin: dict = Depends(require_admin)):
    """Admin-only: switch between shadow and full enforcement."""
    success = _set_deployment_mode(request.admin_id, request.mode, request.effective_date)
    if success:
        settings.DEPLOYMENT_MODE = request.mode
    return {
        "message": f"Deployment mode changing to {request.mode}",
        "success": success,
        "effective_date": request.effective_date,
    }


@router.get("/shadow-config")
async def get_shadow_config():
    """Return what is logged-only vs hard-blocked in shadow mode."""
    config = _get_shadow_mode_config()
    return {"config": config}


@router.put("/shadow-config")
async def update_shadow_config(request: ShadowModeConfigRequest, admin: dict = Depends(require_admin)):
    """Admin-only: adjust shadow mode rules."""
    success = _update_shadow_mode_config(request.admin_id, request.config)
    return {"message": "Shadow mode config updated", "success": success}


@router.get("/readiness-report")
async def get_readiness_report(admin: dict = Depends(require_admin)):
    """Generate shadow-to-enforcement readiness report."""
    report = _generate_readiness_report()
    return report


@router.get("/shadow-vs-enforcement")
async def compare_shadow_vs_enforcement(date_from: str, date_to: str, admin: dict = Depends(require_admin)):
    """Compare what would have been blocked vs what was only logged."""
    comparison = _compare_shadow_vs_enforcement(date_from, date_to)
    return comparison

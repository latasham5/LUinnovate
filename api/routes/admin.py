"""
Admin routes — shadow mode management, deployment config.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from api.dependencies import require_admin

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
    # TODO: enforcer.shadow_mode_service.getDeploymentMode
    return {"mode": "SHADOW"}


@router.put("/deployment-mode")
async def set_deployment_mode(request: DeploymentModeRequest, admin: dict = Depends(require_admin)):
    """Admin-only: switch between shadow and full enforcement."""
    # TODO: enforcer.shadow_mode_service.setDeploymentMode
    return {"message": f"Deployment mode changing to {request.mode}", "effective_date": request.effective_date}


@router.get("/shadow-config")
async def get_shadow_config():
    """Return what is logged-only vs hard-blocked in shadow mode."""
    # TODO: enforcer.shadow_mode_service.getShadowModeConfig
    return {"config": {}}


@router.put("/shadow-config")
async def update_shadow_config(request: ShadowModeConfigRequest, admin: dict = Depends(require_admin)):
    """Admin-only: adjust shadow mode rules."""
    # TODO: enforcer.shadow_mode_service.updateShadowModeConfig
    return {"message": "Shadow mode config updated"}


@router.get("/readiness-report")
async def get_readiness_report(admin: dict = Depends(require_admin)):
    """Generate shadow-to-enforcement readiness report."""
    # TODO: enforcer.shadow_mode_service.generateShadowToEnforcementReadinessReport
    return {"ready": False, "recommendation": "Not enough shadow data collected yet."}


@router.get("/shadow-vs-enforcement")
async def compare_shadow_vs_enforcement(date_from: str, date_to: str, admin: dict = Depends(require_admin)):
    """Compare what would have been blocked vs what was only logged."""
    # TODO: enforcer.shadow_mode_service.compareShadowVsEnforcement
    return {"date_range": {"from": date_from, "to": date_to}, "comparison": {}}

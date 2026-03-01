"""
Policy management routes — CRUD for policy rules, versions, templates.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from api.dependencies import require_admin

router = APIRouter()


class PolicyUpdateRequest(BaseModel):
    """Admin request to update policy rules."""
    admin_id: str
    new_rules: list[dict]
    effective_date: str


@router.get("/active")
async def get_active_policies():
    """Return all currently enforced policy rules and versions."""
    # TODO: enforcer.policy_service.getActivePolicies
    return {"policies": [], "version": "1.0.0"}


@router.get("/category/{category}")
async def get_policy_by_category(category: str):
    """Return rules for a specific risk category."""
    # TODO: enforcer.policy_service.getPolicyByCategory
    return {"category": category, "rules": []}


@router.get("/version")
async def get_policy_version():
    """Return current policy version string."""
    # TODO: enforcer.policy_service.getPolicyVersion
    return {"version": "1.0.0"}


@router.put("/update")
async def update_policy_rules(request: PolicyUpdateRequest, admin: dict = Depends(require_admin)):
    """Admin-only: update policy rules."""
    # TODO: enforcer.policy_service.updatePolicyRules
    return {"message": "Policy update scheduled", "effective_date": request.effective_date}


@router.get("/templates/{role}/{department}")
async def get_allowed_templates(role: str, department: str):
    """Return pre-approved safe prompt templates for a role/department."""
    # TODO: enforcer.policy_service.getAllowedPromptTemplates
    return {"templates": []}


@router.get("/thresholds/{policy_mode}")
async def get_thresholds(policy_mode: str):
    """Return risk thresholds for a specific policy mode."""
    # TODO: enforcer.policy_service.getPolicyThresholdsByMode
    return {"policy_mode": policy_mode, "thresholds": {}}

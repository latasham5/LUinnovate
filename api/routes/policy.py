"""
Policy management routes — CRUD for policy rules, versions, templates.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from api.dependencies import require_admin
from services.enforcer.policy_service import (
    get_active_policies as _get_active_policies,
    get_policy_by_category as _get_policy_by_category,
    get_policy_version as _get_policy_version,
    update_policy_rules as _update_policy_rules,
    get_allowed_prompt_templates as _get_allowed_prompt_templates,
    get_policy_thresholds_by_mode as _get_policy_thresholds_by_mode,
)

router = APIRouter()


class PolicyUpdateRequest(BaseModel):
    """Admin request to update policy rules."""
    admin_id: str
    new_rules: list[dict]
    effective_date: str


@router.get("/active")
async def get_active_policies():
    """Return all currently enforced policy rules and versions."""
    policies = _get_active_policies()
    version = _get_policy_version()
    return {"policies": [p.model_dump() for p in policies], "version": version}


@router.get("/category/{category}")
async def get_policy_by_category(category: str):
    """Return rules for a specific risk category."""
    rules = _get_policy_by_category(category)
    return {"category": category, "rules": [r.model_dump() for r in rules]}


@router.get("/version")
async def get_policy_version():
    """Return current policy version string."""
    version = _get_policy_version()
    return {"version": version}


@router.put("/update")
async def update_policy_rules(request: PolicyUpdateRequest, admin: dict = Depends(require_admin)):
    """Admin-only: update policy rules."""
    success = _update_policy_rules(request.admin_id, request.new_rules, request.effective_date)
    return {
        "message": "Policy update scheduled" if success else "Policy update failed",
        "success": success,
        "effective_date": request.effective_date,
    }


@router.get("/templates/{role}/{department}")
async def get_allowed_templates(role: str, department: str):
    """Return pre-approved safe prompt templates for a role/department."""
    templates = _get_allowed_prompt_templates(role, department)
    return {"templates": templates}


@router.get("/thresholds/{policy_mode}")
async def get_thresholds(policy_mode: str):
    """Return risk thresholds for a specific policy mode."""
    thresholds = _get_policy_thresholds_by_mode(policy_mode)
    return {"policy_mode": policy_mode, "thresholds": thresholds.model_dump()}

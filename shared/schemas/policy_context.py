"""
PolicyContext — Developer 2 -> Developer 1 contract.

Contains active policies, thresholds for the current policy mode,
user profile, and deployment mode.
"""

from typing import Optional
from pydantic import BaseModel
from shared.enums import PolicyMode, DeploymentMode


class UserProfile(BaseModel):
    """Employee profile from Coca-Cola's directory (or mock)."""
    employee_id: str
    name: str
    email: str
    role: str
    department: str
    department_id: str
    clearance_level: str
    manager_id: Optional[str] = None


class PolicyRule(BaseModel):
    """A single policy rule definition."""
    rule_id: str
    category: str
    description: str
    threshold: float
    action: str
    enabled: bool = True


class PolicyThresholds(BaseModel):
    """Risk thresholds adjusted by policy mode."""
    yellow_min: float = 1.0
    yellow_max: float = 39.0
    orange_min: float = 40.0
    orange_max: float = 69.0
    red_min: float = 70.0
    red_max: float = 100.0


class PolicyContext(BaseModel):
    """Complete policy context provided to the Gatekeeper."""

    # User info
    user_profile: UserProfile

    # Active policies
    active_policies: list[PolicyRule] = []
    policy_version: str = "1.0.0"

    # Mode settings
    policy_mode: PolicyMode = PolicyMode.BALANCED
    deployment_mode: DeploymentMode = DeploymentMode.SHADOW

    # Thresholds for current mode
    thresholds: PolicyThresholds = PolicyThresholds()

    # Micro-training trigger threshold for user's department
    training_trigger_threshold: int = 5

"""
Policy Management Service.

loadPolicyDocument, getActivePolicies, getPolicyByCategory,
mapPromptToPolicy, getPolicyVersion, updatePolicyRules,
getAllowedPromptTemplates, validatePolicyConsistency,
getPolicyThresholdsByMode, getMicroTrainingTriggerThreshold.
"""

import json
import os
from typing import Optional
from shared.schemas.policy_context import PolicyContext, PolicyRule, PolicyThresholds, UserProfile
from shared.enums import PolicyMode, DeploymentMode
from config.settings import settings
from config.constants import POLICY_MODE_MULTIPLIERS, DEFAULT_FLAG_THRESHOLD

# Paths
POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "policies")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "prompt_templates")


def load_policy_document(policy_id: str, version_number: str = "latest") -> dict:
    """Fetch a specific policy version from local storage."""
    filepath = os.path.join(POLICIES_DIR, f"{policy_id}.json")
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_active_policies() -> list[PolicyRule]:
    """Return all currently enforced rules and versions."""
    filepath = os.path.join(POLICIES_DIR, "default_policy.json")
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return [PolicyRule(**rule) for rule in data.get("rules", [])]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_policy_by_category(category: str) -> list[PolicyRule]:
    """Return rules for a specific risk category."""
    all_policies = get_active_policies()
    return [p for p in all_policies if p.category == category]


def map_prompt_to_policy(prompt_classification: dict) -> list[PolicyRule]:
    """Determine which policies apply to the detected content."""
    applicable = []
    all_policies = get_active_policies()
    detected_categories = prompt_classification.get("categories", [])

    for policy in all_policies:
        if policy.category in detected_categories and policy.enabled:
            applicable.append(policy)

    return applicable


def get_policy_version() -> str:
    """Return the exact policy version string for audit logging."""
    filepath = os.path.join(POLICIES_DIR, "default_policy.json")
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data.get("version", "1.0.0")
    except (FileNotFoundError, json.JSONDecodeError):
        return "1.0.0"


def update_policy_rules(admin_id: str, new_rules: list[dict], effective_date: str) -> bool:
    """Admin-only: update policy rules."""
    # TODO: Validate admin permissions
    # TODO: Validate policy consistency
    # TODO: Write new rules to storage with effective_date
    return True


def get_allowed_prompt_templates(role: str, department: str) -> list[dict]:
    """Return pre-approved safe prompts for a role/department."""
    filepath = os.path.join(TEMPLATES_DIR, "templates.json")
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            templates = data.get("templates", [])
            return [
                t for t in templates
                if t.get("role", "all") in (role, "all")
                and t.get("department", "all") in (department, "all")
            ]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def validate_policy_consistency(new_rules: list[dict]) -> dict:
    """Check for rule conflicts before activation."""
    # TODO: Detect overlapping or contradictory rules
    return {"valid": True, "conflicts": []}


def get_policy_thresholds_by_mode(policy_mode: str) -> PolicyThresholds:
    """Return adjusted risk thresholds for Strict, Balanced, or Fast mode."""
    multiplier = POLICY_MODE_MULTIPLIERS.get(policy_mode, 1.0)

    return PolicyThresholds(
        yellow_min=1.0,
        yellow_max=39.0 * multiplier,
        orange_min=40.0 * multiplier,
        orange_max=69.0 * multiplier,
        red_min=70.0 * multiplier,
        red_max=100.0,
    )


def get_micro_training_trigger_threshold(department: str) -> int:
    """Return the flag count that triggers training assignment for a department."""
    # TODO: Load department-specific thresholds
    return DEFAULT_FLAG_THRESHOLD


def build_policy_context(user_profile: UserProfile, policy_mode: str = None) -> PolicyContext:
    """
    Build the complete PolicyContext object to send to Developer 1.
    This is the main interface function.
    """
    mode = policy_mode or settings.DEFAULT_POLICY_MODE

    return PolicyContext(
        user_profile=user_profile,
        active_policies=get_active_policies(),
        policy_version=get_policy_version(),
        policy_mode=PolicyMode(mode),
        deployment_mode=DeploymentMode(settings.DEPLOYMENT_MODE),
        thresholds=get_policy_thresholds_by_mode(mode),
        training_trigger_threshold=get_micro_training_trigger_threshold(user_profile.department),
    )

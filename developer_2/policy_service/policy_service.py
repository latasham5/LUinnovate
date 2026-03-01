"""
Policy Management Service
Developer 2 - The Enforcer
"""
import json
import os
from datetime import datetime

POLICIES_PATH = os.path.join(os.path.dirname(__file__), "policies.json")

DEFAULT_POLICIES = {
    "POL-001": {
        "id": "POL-001",
        "version": "1.0.0",
        "category": "credentials",
        "active": True,
        "action": "BLOCK",
        "description": "Block any prompt containing credentials or secrets",
        "thresholds": {"strict": 0.3, "balanced": 0.6, "fast": 0.8}
    },
    "POL-002": {
        "id": "POL-002",
        "version": "1.0.0",
        "category": "pii",
        "active": True,
        "action": "REWRITE",
        "description": "Redact personally identifiable information",
        "thresholds": {"strict": 0.4, "balanced": 0.6, "fast": 0.75}
    },
    "POL-003": {
        "id": "POL-003",
        "version": "1.0.0",
        "category": "trade_secret",
        "active": True,
        "action": "BLOCK",
        "description": "Block prompts containing trade secrets or formulas",
        "thresholds": {"strict": 0.2, "balanced": 0.5, "fast": 0.7}
    },
    "POL-004": {
        "id": "POL-004",
        "version": "1.0.0",
        "category": "financial",
        "active": True,
        "action": "FLAG",
        "description": "Flag prompts with sensitive financial data",
        "thresholds": {"strict": 0.35, "balanced": 0.55, "fast": 0.7}
    }
}

ALLOWED_TEMPLATES = {
    "analyst": ["summarize_report", "market_research", "draft_email"],
    "engineer": ["code_review", "debug_help", "doc_generation"],
    "manager": ["summarize_report", "draft_email", "team_update", "code_review"]
}

MICRO_TRAINING_THRESHOLDS = {
    "marketing": 3,
    "engineering": 5,
    "finance": 2,
    "default": 4
}


def _load_policies() -> dict:
    if os.path.exists(POLICIES_PATH):
        with open(POLICIES_PATH, "r") as f:
            return json.load(f)
    return DEFAULT_POLICIES


def _save_policies(policies: dict):
    with open(POLICIES_PATH, "w") as f:
        json.dump(policies, f, indent=2)


def load_policy_document(policy_id: str, version_number: str = None) -> dict | None:
    """Fetch specific policy version from storage."""
    policies = _load_policies()
    p = policies.get(policy_id)
    if p and (version_number is None or p["version"] == version_number):
        return p
    return None


def get_active_policies() -> list[dict]:
    """Return all currently enforced rules."""
    policies = _load_policies()
    return [p for p in policies.values() if p.get("active")]


def get_policy_by_category(category: str) -> list[dict]:
    """Rules for a specific risk category."""
    policies = _load_policies()
    return [p for p in policies.values() if p["category"] == category and p["active"]]


def map_prompt_to_policy(prompt_classification: str) -> dict | None:
    """Determine which policy applies to detected content type."""
    matches = get_policy_by_category(prompt_classification)
    return matches[0] if matches else None


def get_policy_version() -> str:
    """Aggregate version string for audit logging."""
    policies = _load_policies()
    versions = [f"{k}:{v['version']}" for k, v in policies.items()]
    return "|".join(versions)


def update_policy_rules(admin_id: str, new_rules: dict, effective_date: str) -> dict:
    """Admin-only rule update."""
    policies = _load_policies()
    policy_id = new_rules.get("id")
    if not policy_id:
        return {"success": False, "error": "Missing policy id"}
    new_rules["last_updated_by"] = admin_id
    new_rules["effective_date"] = effective_date
    policies[policy_id] = new_rules
    _save_policies(policies)
    return {"success": True, "policy_id": policy_id}


def get_allowed_prompt_templates(role: str, department: str = None) -> list[str]:
    """Pre-approved safe prompt templates by role."""
    return ALLOWED_TEMPLATES.get(role, [])


def validate_policy_consistency(new_rules: dict) -> dict:
    """Check for rule conflicts before activation."""
    policies = _load_policies()
    conflicts = []
    new_cat = new_rules.get("category")
    for pid, p in policies.items():
        if p["category"] == new_cat and p["active"] and pid != new_rules.get("id"):
            conflicts.append(pid)
    return {"consistent": len(conflicts) == 0, "conflicts": conflicts}


def get_policy_thresholds_by_mode(policy_mode: str) -> dict:
    """Return adjusted risk thresholds for Strict, Balanced, or Fast."""
    mode = policy_mode.lower()
    policies = _load_policies()
    return {
        pid: p["thresholds"].get(mode, p["thresholds"]["balanced"])
        for pid, p in policies.items()
    }


def get_micro_training_trigger_threshold(department: str) -> int:
    """Return flag count that triggers training assignment."""
    return MICRO_TRAINING_THRESHOLDS.get(department, MICRO_TRAINING_THRESHOLDS["default"])


if __name__ == "__main__":
    print("Active Policies:", len(get_active_policies()))
    print("Credentials Policy:", get_policy_by_category("credentials"))
    print("Map 'pii':", map_prompt_to_policy("pii"))
    print("Version:", get_policy_version())
    print("Thresholds (strict):", get_policy_thresholds_by_mode("strict"))
    print("Templates (analyst):", get_allowed_prompt_templates("analyst"))
    print("Training threshold (finance):", get_micro_training_trigger_threshold("finance"))
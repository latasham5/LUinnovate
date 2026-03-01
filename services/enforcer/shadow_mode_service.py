"""
Shadow Mode Management Service.

getDeploymentMode, setDeploymentMode, getShadowModeConfig,
updateShadowModeConfig, generateShadowToEnforcementReadinessReport,
compareShadowVsEnforcement, executeShadowMode.

Uses _prompt_events and _shadow_events from logging_service to compute
analytics. Mode changes are tracked in an in-memory audit log.
"""

import uuid
from collections import defaultdict
from datetime import datetime
from typing import Optional

from shared.enums import ActionType, RiskCategory, SeverityColor
from config.settings import settings
from services.watchtower.logging_service import _prompt_events, _shadow_events


# ---------------------------------------------------------------------------
# In-memory shadow mode config (replace with DB in production)
# ---------------------------------------------------------------------------
_shadow_config: dict = {
    "hard_block": [RiskCategory.CREDENTIALS.value],  # Always blocked even in shadow mode
    "log_only": [
        RiskCategory.FINANCIAL.value,
        RiskCategory.PII.value,
        RiskCategory.CUSTOMER_INFO.value,
        RiskCategory.PROPRIETARY.value,
        RiskCategory.INTERNAL_CODE_NAME.value,
        RiskCategory.REGULATED.value,
    ],
}

# Audit log of mode changes
_mode_change_log: list[dict] = []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_deployment_mode() -> str:
    """Return current deployment mode."""
    return settings.DEPLOYMENT_MODE


def set_deployment_mode(admin_id: str, mode: str, effective_date: str) -> bool:
    """Switch between shadow and full enforcement.

    Validates the mode value, logs the change, and updates the settings object.
    """
    valid_modes = {"SHADOW", "FULL_ENFORCEMENT"}
    if mode not in valid_modes:
        return False

    old_mode = settings.DEPLOYMENT_MODE

    _mode_change_log.append({
        "change_id": f"MODE_{uuid.uuid4().hex[:10]}",
        "admin_id": admin_id,
        "old_mode": old_mode,
        "new_mode": mode,
        "effective_date": effective_date,
        "requested_at": datetime.utcnow().isoformat(),
    })

    # Apply the change to the in-memory settings
    settings.DEPLOYMENT_MODE = mode
    return True


def get_shadow_mode_config() -> dict:
    """Return what is logged-only vs hard-blocked in shadow mode."""
    return _shadow_config.copy()


def update_shadow_mode_config(admin_id: str, config: dict) -> bool:
    """Adjust shadow mode rules.

    Accepts a dict with optional keys 'hard_block' and 'log_only', each
    containing a list of risk category strings.
    """
    global _shadow_config

    # Validate that provided categories are real RiskCategory values
    valid_categories = {rc.value for rc in RiskCategory}
    for key in ("hard_block", "log_only"):
        if key in config:
            for cat in config[key]:
                if cat not in valid_categories:
                    return False

    _mode_change_log.append({
        "change_id": f"CFG_{uuid.uuid4().hex[:10]}",
        "admin_id": admin_id,
        "type": "config_update",
        "old_config": _shadow_config.copy(),
        "new_config": config,
        "requested_at": datetime.utcnow().isoformat(),
    })

    _shadow_config.update(config)
    return True


def execute_shadow_mode(risk_score: float, risk_category: str) -> dict:
    """
    Shadow mode logic:
    - Always blocks credentials regardless of mode
    - Logs everything else
    - Generates "what would have happened" records
    - Still offers safer rewrite suggestions without enforcing
    """
    # Credentials are always blocked
    if risk_category == RiskCategory.CREDENTIALS.value:
        return {
            "action": ActionType.BLOCKED.value,
            "reason": "Credentials blocked even in shadow mode",
            "shadow_logged": True,
        }

    # Check if category is in the hard_block list
    if risk_category in _shadow_config.get("hard_block", []):
        return {
            "action": ActionType.BLOCKED.value,
            "reason": f"{risk_category} is hard-blocked in shadow mode config",
            "shadow_logged": True,
        }

    # Everything else is logged with "what would have happened"
    if risk_score >= 70:
        would_have_been = ActionType.BLOCKED.value
    elif risk_score >= 40:
        would_have_been = ActionType.REWRITTEN.value
    elif risk_score > 0:
        would_have_been = ActionType.ALLOWED_WITH_WARNING.value
    else:
        would_have_been = ActionType.ALLOWED.value

    return {
        "action": ActionType.SHADOW_LOGGED.value,
        "would_have_been": would_have_been,
        "shadow_logged": True,
        "risk_score": risk_score,
    }


def generate_shadow_to_enforcement_readiness_report() -> dict:
    """Analyze shadow data and recommend whether to go live.

    Looks at all shadow-mode events in _prompt_events to calculate:
    - Total events collected
    - Estimated false-positive rate (events with low risk scores that
      would have been blocked/rewritten)
    - A readiness recommendation
    """
    shadow_events = [
        e for e in _prompt_events if e.get("deployment_mode") == "SHADOW"
    ]
    total = len(shadow_events)

    if total == 0:
        return {
            "ready": False,
            "total_shadow_events": 0,
            "estimated_false_positive_rate": 0.0,
            "recommendation": "Insufficient shadow data. Continue collecting.",
        }

    # Estimate false positives: events where the system would have
    # blocked/rewritten but the risk score is relatively low (< 50)
    would_have_acted = [
        e for e in shadow_events
        if e.get("action_taken") in (
            ActionType.BLOCKED.value,
            ActionType.REWRITTEN.value,
            ActionType.SHADOW_LOGGED.value,
        )
    ]
    false_positives = [
        e for e in would_have_acted
        if e.get("risk_score", 0) < 50
    ]

    fp_rate = round((len(false_positives) / len(would_have_acted)) * 100, 2) if would_have_acted else 0.0

    # Readiness criteria:
    # - At least 100 events collected
    # - False positive rate below 15%
    min_events = 100
    max_fp_rate = 15.0
    ready = total >= min_events and fp_rate <= max_fp_rate

    if ready:
        recommendation = (
            f"System is ready for enforcement. {total} events analysed with "
            f"{fp_rate}% estimated false-positive rate."
        )
    elif total < min_events:
        recommendation = (
            f"Only {total} shadow events collected (minimum {min_events} required). "
            f"Continue collecting data."
        )
    else:
        recommendation = (
            f"False-positive rate is {fp_rate}% (target: <{max_fp_rate}%). "
            f"Review detection rules before enabling enforcement."
        )

    return {
        "ready": ready,
        "total_shadow_events": total,
        "estimated_false_positive_rate": fp_rate,
        "would_have_acted_count": len(would_have_acted),
        "estimated_false_positives": len(false_positives),
        "recommendation": recommendation,
    }


def compare_shadow_vs_enforcement(date_from: str, date_to: str) -> dict:
    """Reports showing what would have been blocked vs what was only logged.

    Analyses _prompt_events within the date range for shadow-mode events and
    categorises them by what enforcement action would have been taken.
    """
    events = [
        e for e in _prompt_events
        if e.get("deployment_mode") == "SHADOW"
        and e.get("created_at", "") >= date_from
        and e.get("created_at", "") <= date_to
    ]

    # Also include dedicated _shadow_events in the range
    shadow_extra = [
        e for e in _shadow_events
        if e.get("timestamp", "") >= date_from
        and e.get("timestamp", "") <= date_to
    ]

    total = len(events) + len(shadow_extra)

    # Categorise prompt_events by what would have happened
    would_have_blocked = 0
    would_have_rewritten = 0
    would_have_warned = 0
    only_logged = 0

    for e in events:
        score = e.get("risk_score", 0)
        action = e.get("action_taken", "")
        cat = e.get("risk_category", "")

        # Credentials are always blocked
        if cat == RiskCategory.CREDENTIALS.value or action == ActionType.BLOCKED.value:
            would_have_blocked += 1
        elif score >= 70:
            would_have_blocked += 1
        elif score >= 40:
            would_have_rewritten += 1
        elif score > 0:
            would_have_warned += 1
        else:
            only_logged += 1

    # Categorise shadow_extra by the recorded "what_would_have_happened"
    for se in shadow_extra:
        wwhh = se.get("what_would_have_happened", "")
        if wwhh == ActionType.BLOCKED.value:
            would_have_blocked += 1
        elif wwhh == ActionType.REWRITTEN.value:
            would_have_rewritten += 1
        elif wwhh == ActionType.ALLOWED_WITH_WARNING.value:
            would_have_warned += 1
        else:
            only_logged += 1

    return {
        "date_range": {"from": date_from, "to": date_to},
        "total_events": total,
        "would_have_blocked": would_have_blocked,
        "would_have_rewritten": would_have_rewritten,
        "would_have_warned": would_have_warned,
        "only_logged": only_logged,
    }


# ---------------------------------------------------------------------------
# Dev/testing helpers
# ---------------------------------------------------------------------------

def get_mode_change_log() -> list[dict]:
    """Return the audit log of all mode changes (dev helper)."""
    return _mode_change_log[:]

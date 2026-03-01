"""
Shadow Mode Management Service
Developer 2 - The Enforcer
"""
from datetime import datetime

# In-memory state
_deployment_mode = "SHADOW"  # SHADOW or FULL_ENFORCEMENT

_shadow_config = {
    "hard_block_categories": ["credentials"],
    "log_only_categories": ["pii", "trade_secret", "financial", "general"],
    "offer_rewrite_suggestions": True,
    "collect_false_positive_feedback": True
}

# Simulated shadow history for reporting
_shadow_history = []


def get_deployment_mode() -> str:
    """Return current mode: SHADOW or FULL_ENFORCEMENT."""
    return _deployment_mode


def set_deployment_mode(admin_id: str, mode: str, effective_date: str) -> dict:
    """Switch between shadow and full enforcement."""
    global _deployment_mode
    if mode not in ("SHADOW", "FULL_ENFORCEMENT"):
        return {"success": False, "error": "Invalid mode"}
    prev = _deployment_mode
    _deployment_mode = mode
    return {
        "success": True,
        "previous_mode": prev,
        "new_mode": mode,
        "changed_by": admin_id,
        "effective_date": effective_date
    }


def get_shadow_mode_config() -> dict:
    """Return what is logged-only vs hard-blocked in shadow mode."""
    return _shadow_config.copy()


def update_shadow_mode_config(admin_id: str, config: dict) -> dict:
    """Adjust shadow mode rules."""
    global _shadow_config
    _shadow_config.update(config)
    return {
        "success": True,
        "updated_by": admin_id,
        "timestamp": datetime.utcnow().isoformat(),
        "config": _shadow_config
    }


def record_shadow_event(event: dict):
    """Store a shadow event for later reporting."""
    event["timestamp"] = event.get("timestamp", datetime.utcnow().isoformat())
    _shadow_history.append(event)


def generate_shadow_to_enforcement_readiness_report() -> dict:
    """Analyze shadow data and recommend whether to go live."""
    total = len(_shadow_history)
    if total == 0:
        return {
            "ready": False,
            "reason": "No shadow data collected yet",
            "total_events": 0
        }

    would_block = sum(1 for e in _shadow_history if e.get("would_have_blocked"))
    would_rewrite = sum(1 for e in _shadow_history if e.get("would_have_rewritten"))
    hard_blocked = sum(1 for e in _shadow_history if e.get("hard_blocked"))
    false_pos_rate = 0.0  # Placeholder for real analysis

    ready = total >= 50 and false_pos_rate < 0.05
    return {
        "ready": ready,
        "total_events": total,
        "would_have_blocked": would_block,
        "would_have_rewritten": would_rewrite,
        "hard_blocked_count": hard_blocked,
        "estimated_false_positive_rate": false_pos_rate,
        "recommendation": "GO_LIVE" if ready else "CONTINUE_SHADOW",
        "generated_at": datetime.utcnow().isoformat()
    }


def compare_shadow_vs_enforcement(date_range: tuple[str, str] = None) -> dict:
    """Report: what would have been blocked vs what was only logged."""
    events = _shadow_history
    if date_range:
        start, end = date_range
        events = [e for e in events if start <= e.get("timestamp", "") <= end]

    return {
        "period": date_range or "all_time",
        "total_events": len(events),
        "logged_only": sum(1 for e in events if not e.get("hard_blocked")),
        "hard_blocked": sum(1 for e in events if e.get("hard_blocked")),
        "would_have_blocked": sum(1 for e in events if e.get("would_have_blocked")),
        "would_have_rewritten": sum(1 for e in events if e.get("would_have_rewritten")),
        "passed_through": sum(1 for e in events if not e.get("would_have_blocked") and not e.get("would_have_rewritten"))
    }


if __name__ == "__main__":
    print("Mode:", get_deployment_mode())
    print("Config:", get_shadow_mode_config())

    # Simulate some events
    for i in range(5):
        record_shadow_event({
            "risk_score": 0.7 + i * 0.05,
            "risk_category": "pii",
            "would_have_blocked": True,
            "would_have_rewritten": False,
            "hard_blocked": False
        })
    record_shadow_event({
        "risk_score": 0.95,
        "risk_category": "credentials",
        "would_have_blocked": True,
        "would_have_rewritten": False,
        "hard_blocked": True
    })

    print("\nReadiness:", generate_shadow_to_enforcement_readiness_report())
    print("Comparison:", compare_shadow_vs_enforcement())

    print("\nSwitch mode:", set_deployment_mode("ADMIN01", "FULL_ENFORCEMENT", "2025-03-01"))
    print("New mode:", get_deployment_mode())
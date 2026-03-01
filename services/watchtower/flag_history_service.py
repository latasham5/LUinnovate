"""
User Flag History & Threshold Service.

recordFlagEvent, getUserFlagCount, getUserFlagsByCategory,
checkThreshold, triggerMicroTraining, triggerSupervisorNotification,
getUserRiskTrend, resetFlagCount.

Uses _prompt_events from logging_service as the source of truth and maintains
a lightweight in-memory flag store for reset/audit tracking.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from shared.enums import RiskCategory
from shared.schemas.user_history import UserHistory, CategoryBreakdown
from services.watchtower.logging_service import _prompt_events

# ---------------------------------------------------------------------------
# In-memory stores
# ---------------------------------------------------------------------------

# Extra flag events recorded directly (supplements _prompt_events)
_flag_events: list[dict] = []

# Track flag count resets for audit purposes
_flag_resets: list[dict] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_all_user_events(user_id: str, date_from: str | None = None, date_to: str | None = None) -> list[dict]:
    """Combine _prompt_events and _flag_events for a given user, filtered by date."""
    # From prompt_events: only those that were actually flagged (not plain ALLOWED)
    pe = [
        e for e in _prompt_events
        if e.get("user_id") == user_id and e.get("action_taken") != "ALLOWED"
    ]
    fe = [e for e in _flag_events if e.get("user_id") == user_id]

    combined = pe + fe
    if date_from:
        combined = [e for e in combined if e.get("created_at", e.get("timestamp", "")) >= date_from]
    if date_to:
        combined = [e for e in combined if e.get("created_at", e.get("timestamp", "")) <= date_to]
    return combined


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def record_flag_event(user_id: str, risk_category: str, severity: str, timestamp: str) -> None:
    """Add to the user's running flag history."""
    _flag_events.append({
        "user_id": user_id,
        "risk_category": risk_category,
        "severity": severity,
        "timestamp": timestamp,
        "created_at": timestamp,
    })


async def get_user_flag_count(user_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
    """Total flags in period."""
    events = _get_all_user_events(user_id, date_from, date_to)
    return len(events)


async def get_user_flags_by_category(
    user_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[CategoryBreakdown]:
    """Breakdown by risk category."""
    events = _get_all_user_events(user_id, date_from, date_to)
    counts: dict[str, int] = defaultdict(int)
    for e in events:
        cat = e.get("risk_category", "GENERAL")
        counts[cat] += 1

    result = []
    for cat_str, count in counts.items():
        try:
            category = RiskCategory(cat_str)
        except ValueError:
            category = RiskCategory.GENERAL
        result.append(CategoryBreakdown(category=category, count=count))
    return result


async def check_threshold(user_id: str, flag_count: int, threshold_config: int) -> bool:
    """Evaluate whether training is triggered."""
    return flag_count >= threshold_config


async def trigger_micro_training(user_id: str, relevant_categories: list[str]) -> None:
    """Assign the right training module based on flagged categories."""
    from services.watchtower.training_service import assign_training_module, select_module_by_category

    module_id = select_module_by_category(relevant_categories)
    await assign_training_module(
        user_id=user_id,
        module_id=module_id,
        reason=f"Auto-assigned: flag threshold exceeded for categories {', '.join(relevant_categories)}",
        assigned_timestamp=datetime.utcnow().isoformat(),
    )


async def trigger_supervisor_notification(user_id: str, manager_id: str, flag_summary: dict) -> None:
    """Notify manager with minimal compliant info."""
    from services.watchtower.alerting_service import flag_manager

    summary_text = (
        f"User {user_id} has accumulated {flag_summary.get('total_flags', 0)} flags. "
        f"Top category: {flag_summary.get('top_category', 'N/A')}. "
        f"Trend: {flag_summary.get('trend', 'STABLE')}."
    )
    await flag_manager(
        manager_id=manager_id,
        incident_summary=summary_text,
        timestamp=datetime.utcnow().isoformat(),
    )


async def get_user_risk_trend(user_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> str:
    """Determine if user is improving or worsening over time.

    Compares flag counts in the recent half of the date range vs the older half.
    Returns IMPROVING, STABLE, or WORSENING.
    """
    events = _get_all_user_events(user_id, date_from, date_to)
    if len(events) < 2:
        return "STABLE"

    # Sort by timestamp
    events.sort(key=lambda e: e.get("created_at", e.get("timestamp", "")))

    mid = len(events) // 2
    older_count = mid
    recent_count = len(events) - mid

    if recent_count > older_count * 1.25:
        return "WORSENING"
    elif recent_count < older_count * 0.75:
        return "IMPROVING"
    else:
        return "STABLE"


async def reset_flag_count(user_id: str, reason: str, admin_id: str) -> bool:
    """Authorized reset after training or review.

    Clears the user's entries from _flag_events and logs the reset.
    Note: _prompt_events are immutable audit logs and are NOT cleared.
    """
    global _flag_events
    before_count = len([e for e in _flag_events if e.get("user_id") == user_id])
    _flag_events = [e for e in _flag_events if e.get("user_id") != user_id]

    _flag_resets.append({
        "user_id": user_id,
        "reason": reason,
        "admin_id": admin_id,
        "flags_cleared": before_count,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return True


async def get_user_history(user_id: str) -> UserHistory:
    """
    Build the complete UserHistory object.
    This is the main interface function.
    """
    flag_count = await get_user_flag_count(user_id)
    # Last 30 days
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    flag_count_30d = await get_user_flag_count(user_id, date_from=thirty_days_ago)
    category_breakdown = await get_user_flags_by_category(user_id)
    risk_trend = await get_user_risk_trend(user_id)

    # Compute average risk score from prompt events
    user_events = [e for e in _prompt_events if e.get("user_id") == user_id]
    avg_score = 0.0
    if user_events:
        scores = [e.get("risk_score", 0) for e in user_events]
        avg_score = round(sum(scores) / len(scores), 2)

    # Training status from training service
    from services.watchtower.training_service import _training_completions, _training_assignments
    user_completions = [c for c in _training_completions if c.get("user_id") == user_id]
    user_assignments = [a for a in _training_assignments if a.get("user_id") == user_id]
    pending_modules = [
        a["module_id"] for a in user_assignments
        if a["module_id"] not in {c["module_id"] for c in user_completions}
    ]
    training_completed = len(pending_modules) == 0 and len(user_completions) > 0
    last_training = max(
        (c.get("completion_timestamp", "") for c in user_completions), default=None
    ) if user_completions else None

    return UserHistory(
        user_id=user_id,
        total_flag_count=flag_count,
        flag_count_last_30_days=flag_count_30d,
        category_breakdown=category_breakdown,
        risk_trend=risk_trend,
        training_completed=training_completed,
        pending_training_modules=pending_modules,
        last_training_date=last_training,
        average_risk_score=avg_score,
    )

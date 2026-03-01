"""
user_flag_history_service.py
User Flag History & Threshold Service — tracks per-user flag counts,
evaluates thresholds, triggers training and supervisor notifications.
"""

import uuid
from datetime import datetime
from config import supabase
from models import (
    FlagEvent, ThresholdConfig, SeverityColor,
    DateRangeParams, FlagCountReset,
)


FLAG_HISTORY_TABLE = "user_flag_history"
RESET_LOG_TABLE = "flag_count_resets"


# ── Record & Query ───────────────────────────────────────────────────────

def record_flag_event(event: FlagEvent) -> dict:
    """Append a flag event to the user's running history."""
    data = event.model_dump(mode="json")
    data["id"] = str(uuid.uuid4())
    res = supabase.table(FLAG_HISTORY_TABLE).insert(data).execute()
    return res.data[0]


def get_user_flag_count(user_id: str, date_range: DateRangeParams) -> int:
    """Total flags in period."""
    rows = (
        supabase.table(FLAG_HISTORY_TABLE)
        .select("id", count="exact")
        .eq("user_id", user_id)
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .execute()
    )
    return rows.count or 0


def get_user_flags_by_category(
    user_id: str, date_range: DateRangeParams
) -> dict[str, int]:
    """Breakdown by risk category."""
    rows = (
        supabase.table(FLAG_HISTORY_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .execute()
        .data
    )
    breakdown: dict[str, int] = {}
    for r in rows:
        cat = r.get("risk_category", "unknown")
        breakdown[cat] = breakdown.get(cat, 0) + 1
    return breakdown


def get_user_risk_trend(
    user_id: str, date_range: DateRangeParams
) -> list[dict]:
    """
    Return a time-bucketed trend (weekly counts) so the frontend can
    render a Recharts line chart showing improvement or worsening.
    """
    rows = (
        supabase.table(FLAG_HISTORY_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .order("timestamp")
        .execute()
        .data
    )
    # bucket by ISO week
    buckets: dict[str, int] = {}
    for r in rows:
        ts = datetime.fromisoformat(r["timestamp"])
        week_key = ts.strftime("%Y-W%W")
        buckets[week_key] = buckets.get(week_key, 0) + 1
    return [{"week": k, "count": v} for k, v in sorted(buckets.items())]


# ── Threshold Evaluation ─────────────────────────────────────────────────

def check_threshold(
    user_id: str,
    flag_count: int,
    config: ThresholdConfig,
) -> dict:
    """
    Evaluate whether training or supervisor notification should fire.
    Returns actions to take.
    """
    exceeded = flag_count >= config.max_flags_per_period
    actions: list[str] = []
    if exceeded and config.training_trigger:
        actions.append("trigger_micro_training")
    if exceeded and config.supervisor_notify:
        actions.append("notify_supervisor")
    return {
        "user_id": user_id,
        "flag_count": flag_count,
        "threshold": config.max_flags_per_period,
        "exceeded": exceeded,
        "actions": actions,
    }


def trigger_micro_training(user_id: str, relevant_categories: list[str]) -> dict:
    """
    Placeholder: calls into micro_training_service to assign modules.
    Kept here so the threshold check can invoke it directly.
    """
    from micro_training_service import assign_training_module, select_module_by_category
    module_id = select_module_by_category(relevant_categories)
    return assign_training_module(
        user_id=user_id,
        module_id=module_id,
        reason=f"Threshold exceeded for categories: {', '.join(relevant_categories)}",
    )


def trigger_supervisor_notification(
    user_id: str, manager_id: str, flag_summary: dict
) -> dict:
    """Notify manager with minimal compliant info."""
    from alerting_service import send_notification
    from models import NotificationPayload, NotificationChannel

    msg = (
        f"[Threshold Alert] User {user_id} has accumulated "
        f"{flag_summary.get('total', '?')} flags in the current period."
    )
    return send_notification(NotificationPayload(
        recipient_id=manager_id,
        channel=NotificationChannel.SLACK,
        message=msg,
    ))


# ── Admin Reset ──────────────────────────────────────────────────────────

def reset_flag_count(payload: FlagCountReset) -> dict:
    """Authorized reset after training or review. Audit-logged."""
    log = {
        "id": str(uuid.uuid4()),
        "user_id": payload.user_id,
        "reason": payload.reason,
        "admin_id": payload.admin_id,
        "reset_at": datetime.utcnow().isoformat(),
    }
    supabase.table(RESET_LOG_TABLE).insert(log).execute()
    # Soft-reset: mark existing flags as "reset" rather than deleting
    supabase.table(FLAG_HISTORY_TABLE).update(
        {"reset": True}
    ).eq("user_id", payload.user_id).execute()
    return log

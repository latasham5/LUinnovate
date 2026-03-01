"""
Logging & Audit Service — evidence-friendly, structured logging.

Uses an in-memory store for development. In production, these write to Supabase.
"""

import uuid
from datetime import datetime
from typing import Optional

# In-memory event store (replace with Supabase in production)
_prompt_events: list[dict] = []
_shadow_events: list[dict] = []
_user_sessions: list[dict] = []


async def log_prompt_event(
    user_id: str,
    department_id: str,
    raw_prompt: str,
    analysis,
    policy_context,
    ai_platform: Optional[str] = None,
) -> str:
    """Write the complete structured record. Returns incident_id."""
    incident_id = f"INC_{uuid.uuid4().hex[:12]}"

    event = {
        "incident_id": incident_id,
        "created_at": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "department_id": department_id,
        "risk_category": analysis.detected_categories[0].value if analysis.detected_categories else "GENERAL",
        "risk_score": analysis.risk_score,
        "severity_color": analysis.severity_color.value,
        "confidence_score": analysis.confidence_level.value,
        "action_taken": analysis.recommended_action.value,
        "policy_version": policy_context.policy_version,
        "policy_mode": policy_context.policy_mode.value,
        "deployment_mode": policy_context.deployment_mode.value,
        "detected_elements_summary": [e.text for e in analysis.detected_elements],
        "rewrite_explanation": analysis.rewrite_explanation,
        "detectors_run": analysis.detectors_run,
        "scan_duration_ms": analysis.scan_duration_ms,
        "ai_platform": ai_platform,
    }
    _prompt_events.append(event)
    return incident_id


async def log_user_session(
    user_id: str,
    session_start: str,
    session_end: str,
    total_prompts: int,
    flagged_prompts: int,
) -> None:
    """Session-level tracking."""
    _user_sessions.append({
        "user_id": user_id,
        "session_start": session_start,
        "session_end": session_end,
        "total_prompts": total_prompts,
        "flagged_prompts": flagged_prompts,
    })


async def log_shadow_mode_event(
    user_id: str,
    raw_prompt: str,
    what_would_have_happened: str,
    timestamp: str,
) -> None:
    """Special log for shadow mode events."""
    _shadow_events.append({
        "user_id": user_id,
        "what_would_have_happened": what_would_have_happened,
        "timestamp": timestamp,
    })


async def get_audit_trail(user_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> list[dict]:
    """Retrieve logs for a specific employee."""
    events = [e for e in _prompt_events if e["user_id"] == user_id]
    if date_from:
        events = [e for e in events if e["created_at"] >= date_from]
    if date_to:
        events = [e for e in events if e["created_at"] <= date_to]
    return events


async def get_audit_trail_by_department(
    department_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[dict]:
    """All logs for a department."""
    events = [e for e in _prompt_events if e["department_id"] == department_id]
    if date_from:
        events = [e for e in events if e["created_at"] >= date_from]
    if date_to:
        events = [e for e in events if e["created_at"] <= date_to]
    return events


async def get_audit_trail_by_risk_category(
    category: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[dict]:
    """Filter logs by risk type."""
    events = [e for e in _prompt_events if e["risk_category"] == category]
    if date_from:
        events = [e for e in events if e["created_at"] >= date_from]
    if date_to:
        events = [e for e in events if e["created_at"] <= date_to]
    return events


async def get_audit_trail_by_action(
    action_type: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[dict]:
    """Filter logs by action taken."""
    events = [e for e in _prompt_events if e["action_taken"] == action_type]
    if date_from:
        events = [e for e in events if e["created_at"] >= date_from]
    if date_to:
        events = [e for e in events if e["created_at"] <= date_to]
    return events


async def export_compliance_report(filters: dict, format: str = "json") -> dict:
    """Generate compliance report in CSV, PDF, or JSON."""
    events = _prompt_events[:]
    if filters.get("category"):
        events = [e for e in events if e["risk_category"] == filters["category"]]
    if filters.get("date_from"):
        events = [e for e in events if e["created_at"] >= filters["date_from"]]
    if filters.get("date_to"):
        events = [e for e in events if e["created_at"] <= filters["date_to"]]
    return {"format": format, "records": events, "generated_at": datetime.utcnow().isoformat()}


async def enforce_retention_policy(retention_period_days: int) -> dict:
    """Manage storage duration per compliance requirements."""
    return {"deleted_count": 0, "retention_days": retention_period_days}


async def generate_audit_summary(date_from: Optional[str] = None, date_to: Optional[str] = None) -> dict:
    """Executive-level stats."""
    events = _prompt_events[:]
    if date_from:
        events = [e for e in events if e["created_at"] >= date_from]
    if date_to:
        events = [e for e in events if e["created_at"] <= date_to]

    by_category = {}
    by_action = {}
    by_severity = {}
    for e in events:
        by_category[e["risk_category"]] = by_category.get(e["risk_category"], 0) + 1
        by_action[e["action_taken"]] = by_action.get(e["action_taken"], 0) + 1
        by_severity[e["severity_color"]] = by_severity.get(e["severity_color"], 0) + 1

    flagged = [e for e in events if e["action_taken"] != "ALLOWED"]
    return {
        "total_prompts": len(events),
        "flagged_prompts": len(flagged),
        "flag_rate": len(flagged) / len(events) if events else 0,
        "by_category": by_category,
        "by_action": by_action,
        "by_severity": by_severity,
    }


async def get_flag_record(incident_id: str) -> Optional[dict]:
    """Single record retrieval for investigation."""
    for event in _prompt_events:
        if event["incident_id"] == incident_id:
            return event
    return None

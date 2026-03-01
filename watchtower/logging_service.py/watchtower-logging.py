"""
logging_service.py
Logging & Audit Service — writes, queries, and exports all flag/session records.
"""

import uuid, io, csv, json
from datetime import datetime, timedelta
from config import supabase
from models import (
    FullFlagRecord, UserSession, ShadowModeEvent,
    ExportFormat, DateRangeParams,
)


TABLE = "flag_events"
SESSION_TABLE = "user_sessions"
SHADOW_TABLE = "shadow_mode_events"


# ── Write Operations ─────────────────────────────────────────────────────

def log_prompt_event(record: FullFlagRecord) -> dict:
    """Write the complete structured flag record to the database."""
    data = record.model_dump(mode="json")
    data["incident_id"] = data.get("incident_id") or str(uuid.uuid4())
    res = supabase.table(TABLE).insert(data).execute()
    return res.data[0]


def log_user_session(session: UserSession) -> dict:
    """Session-level tracking."""
    data = session.model_dump(mode="json")
    data["id"] = str(uuid.uuid4())
    res = supabase.table(SESSION_TABLE).insert(data).execute()
    return res.data[0]


def log_shadow_mode_event(event: ShadowModeEvent) -> dict:
    """Special log for shadow-mode events."""
    data = event.model_dump(mode="json")
    data["id"] = str(uuid.uuid4())
    res = supabase.table(SHADOW_TABLE).insert(data).execute()
    return res.data[0]


# ── Read / Query Operations ──────────────────────────────────────────────

def get_audit_trail(user_id: str, date_range: DateRangeParams) -> list[dict]:
    """Retrieve logs for a specific employee."""
    res = (
        supabase.table(TABLE)
        .select("*")
        .eq("user_id", user_id)
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .order("timestamp", desc=True)
        .execute()
    )
    return res.data


def get_audit_trail_by_department(dept_id: str, date_range: DateRangeParams) -> list[dict]:
    res = (
        supabase.table(TABLE)
        .select("*")
        .eq("department_id", dept_id)
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .order("timestamp", desc=True)
        .execute()
    )
    return res.data


def get_audit_trail_by_risk_category(category: str, date_range: DateRangeParams) -> list[dict]:
    res = (
        supabase.table(TABLE)
        .select("*")
        .eq("risk_category", category)
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .order("timestamp", desc=True)
        .execute()
    )
    return res.data


def get_audit_trail_by_action(action_type: str, date_range: DateRangeParams) -> list[dict]:
    res = (
        supabase.table(TABLE)
        .select("*")
        .eq("action_taken", action_type)
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .order("timestamp", desc=True)
        .execute()
    )
    return res.data


def get_flag_record(incident_id: str) -> dict | None:
    """Single record retrieval for investigation."""
    res = supabase.table(TABLE).select("*").eq("incident_id", incident_id).execute()
    return res.data[0] if res.data else None


# ── Export & Compliance ──────────────────────────────────────────────────

def export_compliance_report(
    filters: dict, fmt: ExportFormat
) -> str | list[dict]:
    """
    Generate CSV, PDF placeholder, or JSON export.
    `filters` may include: user_id, department_id, risk_category, action_taken,
    date_start, date_end.
    """
    q = supabase.table(TABLE).select("*")
    if v := filters.get("user_id"):
        q = q.eq("user_id", v)
    if v := filters.get("department_id"):
        q = q.eq("department_id", v)
    if v := filters.get("risk_category"):
        q = q.eq("risk_category", v)
    if v := filters.get("action_taken"):
        q = q.eq("action_taken", v)
    if v := filters.get("date_start"):
        q = q.gte("timestamp", v)
    if v := filters.get("date_end"):
        q = q.lte("timestamp", v)
    rows = q.order("timestamp", desc=True).execute().data

    if fmt == ExportFormat.JSON:
        return rows
    if fmt == ExportFormat.CSV:
        if not rows:
            return ""
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
        return buf.getvalue()
    # PDF would use a library like reportlab — return JSON as placeholder
    return rows


def enforce_retention_policy(retention_period_days: int) -> int:
    """Delete records older than retention period. Returns count deleted."""
    cutoff = (datetime.utcnow() - timedelta(days=retention_period_days)).isoformat()
    res = supabase.table(TABLE).delete().lt("timestamp", cutoff).execute()
    return len(res.data)


def generate_audit_summary(date_range: DateRangeParams) -> dict:
    """Executive-level stats: totals by severity, action, risk category."""
    rows = (
        supabase.table(TABLE)
        .select("*")
        .gte("timestamp", date_range.start.isoformat())
        .lte("timestamp", date_range.end.isoformat())
        .execute()
        .data
    )
    summary = {
        "total_events": len(rows),
        "by_severity": {},
        "by_action": {},
        "by_risk_category": {},
    }
    for r in rows:
        sev = r.get("severity_color", "unknown")
        act = r.get("action_taken", "unknown")
        cat = r.get("risk_category", "unknown")
        summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1
        summary["by_action"][act] = summary["by_action"].get(act, 0) + 1
        summary["by_risk_category"][cat] = summary["by_risk_category"].get(cat, 0) + 1
    return summary

"""
supervisor_access_service.py
Supervisor Data Access Control — governs what detail a manager may see,
enforces access policies, and audit-logs every access event.
"""

import uuid
from datetime import datetime
from config import supabase
from models import DetailRequest, DetailAccessLog


ACCESS_LOG_TABLE = "detail_access_log"
ACCESS_POLICY_TABLE = "detail_access_policies"
INCIDENT_TABLE = "incident_reports"

# Fields that are NEVER exposed to managers
RESTRICTED_FIELDS = {"raw_prompt"}

# Default fields a manager may see
DEFAULT_APPROVED_FIELDS = [
    "incident_id",
    "risk_category",
    "severity_color",
    "action_taken",
    "timestamp",
    "prompt_summary",
    "confidence_score",
]


# ── Policy Evaluation ────────────────────────────────────────────────────

def evaluate_detail_access_policy(
    manager_id: str, incident_id: str
) -> dict:
    """
    Check whether the manager is authorized to view deeper detail
    for this incident. Returns the list of approved fields.
    """
    # Look up department-level or role-level policy
    policy = (
        supabase.table(ACCESS_POLICY_TABLE)
        .select("*")
        .eq("manager_id", manager_id)
        .execute()
        .data
    )
    if policy:
        approved = policy[0].get("approved_fields", DEFAULT_APPROVED_FIELDS)
    else:
        approved = DEFAULT_APPROVED_FIELDS

    # Ensure restricted fields are never included
    approved = [f for f in approved if f not in RESTRICTED_FIELDS]

    return {
        "manager_id": manager_id,
        "incident_id": incident_id,
        "access_granted": True,
        "approved_fields": approved,
    }


# ── Detail Retrieval ─────────────────────────────────────────────────────

def get_approved_incident_detail(
    incident_id: str, approved_fields: list[str]
) -> dict | None:
    """Return only the fields the manager is authorized to see."""
    res = (
        supabase.table(INCIDENT_TABLE)
        .select("*")
        .eq("incident_id", incident_id)
        .execute()
    )
    if not res.data:
        return None
    full = res.data[0]
    return {k: v for k, v in full.items() if k in approved_fields}


# ── Request Handling (Orchestrator) ──────────────────────────────────────

def handle_detail_request(req: DetailRequest) -> dict:
    """
    Full flow: evaluate policy → fetch approved fields → audit log.
    """
    policy = evaluate_detail_access_policy(req.manager_id, req.incident_id)
    if not policy["access_granted"]:
        return {"error": "Access denied", "manager_id": req.manager_id}

    detail = get_approved_incident_detail(
        req.incident_id, policy["approved_fields"]
    )

    log_detail_access_event(
        manager_id=req.manager_id,
        incident_id=req.incident_id,
        approved_fields=policy["approved_fields"],
    )

    return {
        "incident_id": req.incident_id,
        "approved_fields": policy["approved_fields"],
        "detail": detail,
        "justification_recorded": req.justification,
    }


# ── Audit Logging ────────────────────────────────────────────────────────

def log_detail_access_event(
    manager_id: str,
    incident_id: str,
    approved_fields: list[str],
) -> dict:
    """Audit: who accessed what and when."""
    entry = {
        "id": str(uuid.uuid4()),
        "manager_id": manager_id,
        "incident_id": incident_id,
        "approved_fields": approved_fields,
        "timestamp": datetime.utcnow().isoformat(),
    }
    supabase.table(ACCESS_LOG_TABLE).insert(entry).execute()
    return entry

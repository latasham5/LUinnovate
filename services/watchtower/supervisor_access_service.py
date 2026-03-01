"""
Supervisor Data Access Control.

handleDetailRequest, evaluateDetailAccessPolicy,
getApprovedIncidentDetail, logDetailAccessEvent.

Uses in-memory stores for access logs and manager-department mappings.
Incident data is pulled from logging_service._prompt_events.
"""

import uuid
from datetime import datetime

from services.watchtower.logging_service import _prompt_events

# ---------------------------------------------------------------------------
# In-memory stores
# ---------------------------------------------------------------------------

# Audit log of every time a manager accessed incident detail
_detail_access_log: list[dict] = []

# Manager-to-department mapping (manager_id -> set of department_ids they manage)
# Pre-populated with a permissive default for development
_manager_departments: dict[str, set[str]] = {}

# Role-based access rules: role -> list of fields they can see
_role_access_rules: dict[str, list[str]] = {
    "manager": ["risk_category", "action_taken", "severity_color", "timestamp", "department_id"],
    "security_admin": [
        "risk_category", "action_taken", "severity_color", "timestamp",
        "department_id", "confidence_score", "policy_version", "detected_elements_summary",
    ],
    "compliance_officer": [
        "risk_category", "action_taken", "severity_color", "timestamp",
        "department_id", "confidence_score", "policy_version", "policy_mode",
        "deployment_mode",
    ],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def handle_detail_request(manager_id: str, incident_id: str, justification: str) -> dict:
    """Process manager's request to see more incident detail."""
    # Step 1: Evaluate if the manager has access
    access_allowed = await evaluate_detail_access_policy(manager_id, incident_id)

    if not access_allowed:
        # Log the denied attempt too
        await log_detail_access_event(
            manager_id=manager_id,
            incident_id=incident_id,
            timestamp=datetime.utcnow().isoformat(),
            access_granted=False,
            justification=justification,
        )
        return {
            "status": "denied",
            "reason": "Access policy does not permit viewing this incident detail.",
        }

    # Step 2: Get the approved fields
    approved_fields = ["risk_category", "action_taken", "severity_color", "timestamp", "department_id"]
    detail = await get_approved_incident_detail(incident_id, approved_fields)

    # Step 3: Log the access event
    await log_detail_access_event(
        manager_id=manager_id,
        incident_id=incident_id,
        timestamp=datetime.utcnow().isoformat(),
        access_granted=True,
        justification=justification,
    )

    return {"status": "approved", "detail": detail}


async def evaluate_detail_access_policy(manager_id: str, incident_id: str) -> bool:
    """Check if policy allows the manager deeper access to this incident.

    Rules:
    1. Find the incident's department_id
    2. Verify the manager manages that department
    3. In dev mode, if no mappings exist, allow access by default
    """
    # Find the incident
    incident = None
    for event in _prompt_events:
        if event.get("incident_id") == incident_id:
            incident = event
            break

    if incident is None:
        # Incident not found -- deny access
        return False

    incident_dept = incident.get("department_id", "")

    # If no manager-department mappings configured, default allow (dev mode)
    if not _manager_departments:
        return True

    # Check if manager manages the incident's department
    managed_depts = _manager_departments.get(manager_id, set())
    return incident_dept in managed_depts


async def get_approved_incident_detail(incident_id: str, approved_fields: list[str]) -> dict:
    """Return only the fields the manager is authorized to see."""
    # Find the incident in _prompt_events
    incident = None
    for event in _prompt_events:
        if event.get("incident_id") == incident_id:
            incident = event
            break

    if incident is None:
        return {field: "not_found" for field in approved_fields}

    # Filter to only approved fields
    return {field: incident.get(field, "N/A") for field in approved_fields}


async def log_detail_access_event(
    manager_id: str,
    incident_id: str,
    timestamp: str,
    access_granted: bool = True,
    justification: str = "",
) -> None:
    """Audit log of who accessed what incident detail and when."""
    _detail_access_log.append({
        "access_id": f"ACCESS_{uuid.uuid4().hex[:10]}",
        "manager_id": manager_id,
        "incident_id": incident_id,
        "timestamp": timestamp,
        "access_granted": access_granted,
        "justification": justification,
    })


# ---------------------------------------------------------------------------
# Admin / configuration helpers
# ---------------------------------------------------------------------------

def register_manager_department(manager_id: str, department_id: str) -> None:
    """Register that a manager oversees a given department."""
    if manager_id not in _manager_departments:
        _manager_departments[manager_id] = set()
    _manager_departments[manager_id].add(department_id)


def get_access_audit_log(manager_id: str | None = None) -> list[dict]:
    """Retrieve the access audit log, optionally filtered by manager."""
    if manager_id:
        return [e for e in _detail_access_log if e["manager_id"] == manager_id]
    return _detail_access_log[:]


def get_fields_for_role(role: str) -> list[str]:
    """Return the list of incident fields visible to a given role."""
    return _role_access_rules.get(role, _role_access_rules["manager"])

"""
Audit trail routes — log queries, compliance exports, incident details.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from api.dependencies import get_current_user, require_elevated
from services.watchtower.logging_service import (
    get_audit_trail as _get_audit_trail,
    get_audit_trail_by_department as _get_audit_trail_by_department,
    get_audit_trail_by_risk_category as _get_audit_trail_by_risk_category,
    get_audit_trail_by_action as _get_audit_trail_by_action,
    get_flag_record as _get_flag_record,
    generate_audit_summary as _generate_audit_summary,
    export_compliance_report as _export_compliance_report,
)

router = APIRouter()


@router.get("/user/{user_id}")
async def get_user_audit_trail(user_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Retrieve logs for a specific employee."""
    events = await _get_audit_trail(user_id, date_from, date_to)
    return {"user_id": user_id, "events": events}


@router.get("/department/{department_id}")
async def get_department_audit_trail(department_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """All logs for a department."""
    events = await _get_audit_trail_by_department(department_id, date_from, date_to)
    return {"department_id": department_id, "events": events}


@router.get("/category/{category}")
async def get_audit_by_category(category: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Filter logs by risk category."""
    events = await _get_audit_trail_by_risk_category(category, date_from, date_to)
    return {"category": category, "events": events}


@router.get("/action/{action_type}")
async def get_audit_by_action(action_type: str, date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Filter logs by action taken."""
    events = await _get_audit_trail_by_action(action_type, date_from, date_to)
    return {"action_type": action_type, "events": events}


@router.get("/incident/{incident_id}")
async def get_flag_record(incident_id: str, current_user: dict = Depends(require_elevated)):
    """Single record retrieval for investigation."""
    record = await _get_flag_record(incident_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return {"incident_id": incident_id, "record": record}


@router.get("/summary")
async def get_audit_summary(date_from: Optional[str] = None, date_to: Optional[str] = None, current_user: dict = Depends(require_elevated)):
    """Executive-level stats."""
    summary = await _generate_audit_summary(date_from, date_to)
    return {"summary": summary}


@router.get("/export")
async def export_compliance_report(
    format: str = "json",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(require_elevated),
):
    """Generate compliance report in CSV, PDF, or JSON."""
    filters = {}
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    if category:
        filters["category"] = category
    report = await _export_compliance_report(filters, format)
    return report


@router.get("/supervisor/request-detail")
async def request_incident_detail(
    manager_id: str,
    incident_id: str,
    justification: str,
    current_user: dict = Depends(require_elevated),
):
    """Manager requests to see more detail on an incident."""
    return {"status": "approved", "manager_id": manager_id, "incident_id": incident_id}

"""
Alerting & Escalation Service.

flagManager, flagCybersecurityTeam, createIncidentReport,
escalateBySeverity, sendNotification, createTicket,
checkEscalationRules, generatePrivacySafeManagerAlert.

In development mode all alerts are stored in an in-memory list rather than
being dispatched via Slack / Teams webhooks.
"""

import uuid
from datetime import datetime
from typing import Optional

from shared.enums import SeverityColor

# ---------------------------------------------------------------------------
# In-memory stores (replace with real integrations in production)
# ---------------------------------------------------------------------------
_alerts: list[dict] = []          # every alert sent
_incidents: list[dict] = []       # structured incident reports
_tickets: list[dict] = []         # tickets created for red-level events

# Per-department escalation rule overrides
_escalation_rules: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def flag_manager(manager_id: str, incident_summary: str, timestamp: str) -> None:
    """Send a privacy-safe alert to the manager.

    Dev mode: appends to _alerts instead of calling a Slack/Teams webhook.
    """
    alert = {
        "alert_id": f"ALERT_{uuid.uuid4().hex[:10]}",
        "type": "manager_notification",
        "recipient_id": manager_id,
        "channel": "slack",
        "message": incident_summary,
        "timestamp": timestamp or datetime.utcnow().isoformat(),
        "delivered": True,  # simulated
    }
    _alerts.append(alert)


async def flag_cybersecurity_team(
    team_id: str,
    incident_details: dict,
    severity: str,
    timestamp: str,
) -> None:
    """Send full context alert to the security team.

    Dev mode: appends to _alerts instead of calling a webhook.
    """
    alert = {
        "alert_id": f"ALERT_{uuid.uuid4().hex[:10]}",
        "type": "cybersecurity_alert",
        "recipient_id": team_id,
        "channel": "teams",
        "severity": severity,
        "incident_details": incident_details,
        "timestamp": timestamp or datetime.utcnow().isoformat(),
        "delivered": True,  # simulated
    }
    _alerts.append(alert)


def create_incident_report(
    user_id: str,
    prompt: str,
    risk_category: str,
    action_taken: str,
    policy_version: str,
    confidence_score: str,
    timestamp: str,
    severity_color: str,
) -> dict:
    """Create a structured incident record and store it in memory."""
    report = {
        "incident_id": f"INC_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "user_id": user_id,
        "risk_category": risk_category,
        "action_taken": action_taken,
        "policy_version": policy_version,
        "confidence_score": confidence_score,
        "timestamp": timestamp,
        "severity_color": severity_color,
        "prompt_length": len(prompt),
    }
    _incidents.append(report)
    return report


async def escalate_by_severity(severity_color: str, incident_report: dict) -> None:
    """
    Route alerts based on severity color:
    - Yellow: log only, include in weekly digest
    - Orange: real-time manager notification
    - Red: immediate manager AND cybersecurity alert + ticket creation
    """
    if severity_color == SeverityColor.YELLOW.value:
        # Log only -- will appear in weekly digest
        _alerts.append({
            "alert_id": f"ALERT_{uuid.uuid4().hex[:10]}",
            "type": "digest_log",
            "severity": severity_color,
            "incident_id": incident_report.get("incident_id", ""),
            "timestamp": incident_report.get("timestamp", datetime.utcnow().isoformat()),
            "delivered": False,  # queued for digest
        })

    elif severity_color == SeverityColor.ORANGE.value:
        # Real-time manager notification
        await flag_manager(
            manager_id=incident_report.get("manager_id", ""),
            incident_summary=generate_privacy_safe_manager_alert(incident_report),
            timestamp=incident_report.get("timestamp", ""),
        )

    elif severity_color == SeverityColor.RED.value:
        # Immediate manager AND cybersecurity alert
        await flag_manager(
            manager_id=incident_report.get("manager_id", ""),
            incident_summary=generate_privacy_safe_manager_alert(incident_report),
            timestamp=incident_report.get("timestamp", ""),
        )
        await flag_cybersecurity_team(
            team_id=incident_report.get("security_team_id", ""),
            incident_details=incident_report,
            severity=severity_color,
            timestamp=incident_report.get("timestamp", ""),
        )
        # Auto-create a ticket for red-level events
        await create_ticket(incident_report, system="internal")


async def send_notification(recipient_id: str, channel: str, message: str) -> bool:
    """Dispatch notification via Slack webhook or Teams.

    Dev mode: stores in _alerts. Returns True to indicate success.
    """
    alert = {
        "alert_id": f"ALERT_{uuid.uuid4().hex[:10]}",
        "type": "notification",
        "recipient_id": recipient_id,
        "channel": channel,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "delivered": True,  # simulated
    }
    _alerts.append(alert)
    return True


async def create_ticket(incident_report: dict, system: str = "internal") -> str:
    """Create incident ticket for red-level events.

    Dev mode: stores ticket in-memory and returns a ticket ID.
    """
    ticket_id = f"TICKET_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    ticket = {
        "ticket_id": ticket_id,
        "system": system,
        "incident_id": incident_report.get("incident_id", ""),
        "severity": incident_report.get("severity_color", ""),
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
        "incident_report": incident_report,
    }
    _tickets.append(ticket)
    return ticket_id


def check_escalation_rules(department_id: str, incident_type: str) -> dict:
    """Get custom escalation flows per department.

    If the department has a custom rule set, return it; otherwise fall back to
    the default escalation path.
    """
    default_rules = {
        "escalation_path": ["manager", "security_team"],
        "auto_ticket": True,
        "notify_channels": ["slack"],
    }

    dept_rules = _escalation_rules.get(department_id)
    if dept_rules:
        # Merge with defaults -- department overrides win
        merged = {**default_rules, **dept_rules}
        # Filter by incident type if the rules specify per-type paths
        if "incident_type_overrides" in merged and incident_type in merged["incident_type_overrides"]:
            merged["escalation_path"] = merged["incident_type_overrides"][incident_type]
        return merged

    return default_rules


def generate_privacy_safe_manager_alert(incident_report: dict) -> str:
    """Strip raw prompt, keep only summary info for manager notification."""
    return (
        f"Security alert: A {incident_report.get('severity_color', 'UNKNOWN')} severity event "
        f"was detected in the {incident_report.get('risk_category', 'UNKNOWN')} category. "
        f"Action taken: {incident_report.get('action_taken', 'UNKNOWN')}."
    )


# ---------------------------------------------------------------------------
# Utility functions for dev/testing
# ---------------------------------------------------------------------------

def get_all_alerts() -> list[dict]:
    """Return all in-memory alerts (dev helper)."""
    return _alerts[:]


def get_all_tickets() -> list[dict]:
    """Return all in-memory tickets (dev helper)."""
    return _tickets[:]


def get_all_incidents() -> list[dict]:
    """Return all in-memory incident reports (dev helper)."""
    return _incidents[:]

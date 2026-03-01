"""
alerting_service.py
Alerting & Escalation Service — routes incidents by severity, dispatches
notifications, and creates tickets.
"""

import uuid, httpx
from datetime import datetime
from config import supabase, SLACK_WEBHOOK_URL, TEAMS_WEBHOOK_URL
from models import (
    IncidentReport, ManagerAlert, CybersecurityAlert,
    NotificationPayload, NotificationChannel, SeverityColor,
)


INCIDENT_TABLE = "incident_reports"
ESCALATION_RULES_TABLE = "escalation_rules"


# ── Incident Creation ────────────────────────────────────────────────────

def create_incident_report(report: IncidentReport) -> dict:
    """Persist a structured incident record."""
    data = report.model_dump(mode="json")
    data["incident_id"] = data.get("incident_id") or str(uuid.uuid4())
    res = supabase.table(INCIDENT_TABLE).insert(data).execute()
    return res.data[0]


# ── Notification Dispatch ────────────────────────────────────────────────

def send_notification(payload: NotificationPayload) -> dict:
    """
    Dispatch notification via the appropriate channel.
    Holds the Slack/Teams webhook URLs.
    """
    msg = {
        "recipient_id": payload.recipient_id,
        "text": payload.message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if payload.channel == NotificationChannel.SLACK:
        _post_webhook(SLACK_WEBHOOK_URL, msg)
    elif payload.channel == NotificationChannel.TEAMS:
        _post_webhook(TEAMS_WEBHOOK_URL, msg)
    else:
        # EMAIL: integrate with your SMTP / SendGrid / SES here
        pass

    return {"status": "sent", **msg}


def _post_webhook(url: str, body: dict) -> None:
    if not url:
        return
    with httpx.Client(timeout=10) as client:
        client.post(url, json=body)


# ── Manager & Security Alerts ────────────────────────────────────────────

def flag_manager(alert: ManagerAlert) -> dict:
    """Privacy-safe alert to manager (no raw prompt)."""
    return send_notification(
        NotificationPayload(
            recipient_id=alert.manager_id,
            channel=NotificationChannel.SLACK,
            message=f"[Manager Alert] {alert.incident_summary}",
        )
    )


def flag_cybersecurity_team(alert: CybersecurityAlert) -> dict:
    """Full-context alert to security team."""
    return send_notification(
        NotificationPayload(
            recipient_id=alert.team_id,
            channel=NotificationChannel.SLACK,
            message=(
                f"[SECURITY {alert.severity.value.upper()}] "
                f"{alert.incident_details}"
            ),
        )
    )


# ── Privacy-Safe Alert Generation ────────────────────────────────────────

def generate_privacy_safe_manager_alert(report: IncidentReport) -> dict:
    """Strip raw prompt, keep only summary info for the manager."""
    return {
        "incident_id": report.incident_id,
        "risk_category": report.risk_category,
        "severity_color": report.severity_color.value,
        "action_taken": report.action_taken.value,
        "timestamp": report.timestamp.isoformat(),
        "summary": report.prompt_summary or "Flagged prompt — details restricted.",
    }


# ── Severity-Based Escalation ───────────────────────────────────────────

def escalate_by_severity(
    severity: SeverityColor,
    report: IncidentReport,
    manager_id: str | None = None,
    security_team_id: str | None = None,
) -> dict:
    """
    Route based on severity color:
      Yellow  → log only, included in weekly digest
      Orange  → real-time manager notification
      Red     → immediate manager AND cybersecurity alert
    """
    actions_taken: list[str] = []

    if severity == SeverityColor.YELLOW:
        actions_taken.append("logged_for_weekly_digest")

    elif severity == SeverityColor.ORANGE:
        if manager_id:
            safe = generate_privacy_safe_manager_alert(report)
            flag_manager(ManagerAlert(
                manager_id=manager_id,
                incident_summary=safe["summary"],
                timestamp=report.timestamp,
            ))
            actions_taken.append("manager_notified")

    elif severity == SeverityColor.RED:
        if manager_id:
            safe = generate_privacy_safe_manager_alert(report)
            flag_manager(ManagerAlert(
                manager_id=manager_id,
                incident_summary=safe["summary"],
                timestamp=report.timestamp,
            ))
            actions_taken.append("manager_notified")
        if security_team_id:
            flag_cybersecurity_team(CybersecurityAlert(
                team_id=security_team_id,
                incident_details=report.model_dump(mode="json"),
                severity=severity,
                timestamp=report.timestamp,
            ))
            actions_taken.append("cybersecurity_notified")
        actions_taken.append("ticket_created")

    return {
        "incident_id": report.incident_id,
        "severity": severity.value,
        "actions_taken": actions_taken,
    }


# ── Ticket Creation ─────────────────────────────────────────────────────

def create_ticket(report: IncidentReport, system: str = "internal") -> dict:
    """Create an incident ticket for red-level events."""
    ticket = {
        "ticket_id": str(uuid.uuid4()),
        "incident_id": report.incident_id,
        "system": system,
        "created_at": datetime.utcnow().isoformat(),
        "status": "open",
        "severity": report.severity_color.value,
    }
    supabase.table("incident_tickets").insert(ticket).execute()
    return ticket


# ── Department Escalation Rules ──────────────────────────────────────────

def check_escalation_rules(department_id: str, incident_type: str) -> dict | None:
    """Retrieve custom escalation flow for a department + incident type."""
    res = (
        supabase.table(ESCALATION_RULES_TABLE)
        .select("*")
        .eq("department_id", department_id)
        .eq("incident_type", incident_type)
        .execute()
    )
    return res.data[0] if res.data else None

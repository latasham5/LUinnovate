"""
routes.py
FastAPI routers exposing all Watchtower services to the React + Vite frontend.
All endpoints return JSON consumed by the TypeScript client.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime

from models import (
    FullFlagRecord, UserSession, ShadowModeEvent,
    IncidentReport, ManagerAlert, CybersecurityAlert,
    NotificationPayload, SeverityColor, ExportFormat,
    FlagEvent, ThresholdConfig, FlagCountReset,
    QuizResponse, TrainingCompletion, DateRangeParams,
    DetailRequest,
)

import logging_service as log_svc
import alerting_service as alert_svc
import user_flag_history_service as flag_svc
import micro_training_service as train_svc
import scorecard_service as score_svc
import supervisor_access_service as sup_svc


# ── Helper ───────────────────────────────────────────────────────────────

def _dr(start: str, end: str) -> DateRangeParams:
    return DateRangeParams(
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
    )


# ═══════════════════════════════════════════════════════════════════════════
#  1. LOGGING & AUDIT
# ═══════════════════════════════════════════════════════════════════════════

audit_router = APIRouter(prefix="/api/audit", tags=["Audit & Logging"])


@audit_router.post("/log-event")
def log_event(record: FullFlagRecord):
    return log_svc.log_prompt_event(record)


@audit_router.post("/log-session")
def log_session(session: UserSession):
    return log_svc.log_user_session(session)


@audit_router.post("/log-shadow")
def log_shadow(event: ShadowModeEvent):
    return log_svc.log_shadow_mode_event(event)


@audit_router.get("/trail/user/{user_id}")
def get_user_trail(user_id: str, start: str = Query(...), end: str = Query(...)):
    return log_svc.get_audit_trail(user_id, _dr(start, end))


@audit_router.get("/trail/department/{dept_id}")
def get_dept_trail(dept_id: str, start: str = Query(...), end: str = Query(...)):
    return log_svc.get_audit_trail_by_department(dept_id, _dr(start, end))


@audit_router.get("/trail/risk-category/{category}")
def get_category_trail(category: str, start: str = Query(...), end: str = Query(...)):
    return log_svc.get_audit_trail_by_risk_category(category, _dr(start, end))


@audit_router.get("/trail/action/{action_type}")
def get_action_trail(action_type: str, start: str = Query(...), end: str = Query(...)):
    return log_svc.get_audit_trail_by_action(action_type, _dr(start, end))


@audit_router.get("/record/{incident_id}")
def get_record(incident_id: str):
    rec = log_svc.get_flag_record(incident_id)
    if not rec:
        raise HTTPException(404, "Record not found")
    return rec


@audit_router.get("/export")
def export_report(
    fmt: ExportFormat = Query(ExportFormat.JSON),
    user_id: Optional[str] = None,
    department_id: Optional[str] = None,
    risk_category: Optional[str] = None,
    action_taken: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
):
    filters = {
        k: v for k, v in {
            "user_id": user_id, "department_id": department_id,
            "risk_category": risk_category, "action_taken": action_taken,
            "date_start": date_start, "date_end": date_end,
        }.items() if v
    }
    return log_svc.export_compliance_report(filters, fmt)


@audit_router.post("/retention")
def enforce_retention(retention_period_days: int = Query(365)):
    deleted = log_svc.enforce_retention_policy(retention_period_days)
    return {"deleted_count": deleted}


@audit_router.get("/summary")
def audit_summary(start: str = Query(...), end: str = Query(...)):
    return log_svc.generate_audit_summary(_dr(start, end))


# ═══════════════════════════════════════════════════════════════════════════
#  2. ALERTING & ESCALATION
# ═══════════════════════════════════════════════════════════════════════════

alert_router = APIRouter(prefix="/api/alerts", tags=["Alerting & Escalation"])


@alert_router.post("/incident")
def create_incident(report: IncidentReport):
    return alert_svc.create_incident_report(report)


@alert_router.post("/notify")
def notify(payload: NotificationPayload):
    return alert_svc.send_notification(payload)


@alert_router.post("/flag-manager")
def notify_manager(alert: ManagerAlert):
    return alert_svc.flag_manager(alert)


@alert_router.post("/flag-security")
def notify_security(alert: CybersecurityAlert):
    return alert_svc.flag_cybersecurity_team(alert)


@alert_router.post("/escalate")
def escalate(
    report: IncidentReport,
    manager_id: Optional[str] = Query(None),
    security_team_id: Optional[str] = Query(None),
):
    return alert_svc.escalate_by_severity(
        report.severity_color, report, manager_id, security_team_id
    )


@alert_router.post("/ticket")
def create_ticket(report: IncidentReport, system: str = Query("internal")):
    return alert_svc.create_ticket(report, system)


@alert_router.get("/escalation-rules/{dept_id}")
def escalation_rules(dept_id: str, incident_type: str = Query(...)):
    rules = alert_svc.check_escalation_rules(dept_id, incident_type)
    if not rules:
        raise HTTPException(404, "No rules found")
    return rules


# ═══════════════════════════════════════════════════════════════════════════
#  3. USER FLAG HISTORY & THRESHOLD
# ═══════════════════════════════════════════════════════════════════════════

flag_router = APIRouter(prefix="/api/flags", tags=["User Flag History"])


@flag_router.post("/record")
def record_flag(event: FlagEvent):
    return flag_svc.record_flag_event(event)


@flag_router.get("/count/{user_id}")
def flag_count(user_id: str, start: str = Query(...), end: str = Query(...)):
    return {"user_id": user_id, "count": flag_svc.get_user_flag_count(user_id, _dr(start, end))}


@flag_router.get("/by-category/{user_id}")
def flags_by_category(user_id: str, start: str = Query(...), end: str = Query(...)):
    return flag_svc.get_user_flags_by_category(user_id, _dr(start, end))


@flag_router.get("/trend/{user_id}")
def risk_trend(user_id: str, start: str = Query(...), end: str = Query(...)):
    return flag_svc.get_user_risk_trend(user_id, _dr(start, end))


@flag_router.post("/check-threshold")
def check_threshold(user_id: str, flag_count: int, config: ThresholdConfig):
    return flag_svc.check_threshold(user_id, flag_count, config)


@flag_router.post("/reset")
def reset_flags(payload: FlagCountReset):
    return flag_svc.reset_flag_count(payload)


# ═══════════════════════════════════════════════════════════════════════════
#  4. MICRO-TRAINING
# ═══════════════════════════════════════════════════════════════════════════

training_router = APIRouter(prefix="/api/training", tags=["Micro-Training"])


@training_router.post("/assign")
def assign_module(user_id: str, module_id: str, reason: str = "manual"):
    return train_svc.assign_training_module(user_id, module_id, reason)


@training_router.get("/module/{module_id}")
def get_module(module_id: str):
    content = train_svc.get_training_module_content(module_id)
    if not content:
        raise HTTPException(404, "Module not found")
    return content


@training_router.get("/select-module")
def select_module(categories: str = Query(..., description="Comma-separated risk categories")):
    cats = [c.strip() for c in categories.split(",")]
    return {"module_id": train_svc.select_module_by_category(cats)}


@training_router.post("/quiz-response")
def quiz_response(resp: QuizResponse):
    return train_svc.record_quiz_response(resp)


@training_router.post("/evaluate")
def evaluate_quiz(user_id: str, module_id: str, responses: list[QuizResponse]):
    return train_svc.evaluate_quiz_completion(user_id, module_id, responses)


@training_router.post("/remind")
def remind(user_id: str, module_id: str, days_overdue: int = 1):
    return train_svc.send_training_reminder(user_id, module_id, days_overdue)


@training_router.get("/history/{user_id}")
def training_history(user_id: str):
    return train_svc.get_training_history(user_id)


@training_router.get("/effectiveness/{module_id}")
def effectiveness(module_id: str, start: str = Query(...), end: str = Query(...)):
    return train_svc.generate_training_effectiveness_report(module_id, _dr(start, end))


# ═══════════════════════════════════════════════════════════════════════════
#  5. SCORECARD & ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

scorecard_router = APIRouter(prefix="/api/scorecard", tags=["Scorecard & Analytics"])


@scorecard_router.get("/department/{dept_id}")
def dept_score(dept_id: str, start: str = Query(...), end: str = Query(...)):
    return score_svc.calculate_department_score(dept_id, _dr(start, end)).model_dump(mode="json")


@scorecard_router.get("/department/{dept_id}/breakdown")
def dept_breakdown(dept_id: str, start: str = Query(...), end: str = Query(...)):
    return score_svc.get_department_breakdown(dept_id, _dr(start, end))


@scorecard_router.get("/department/{dept_id}/top-offenders")
def top_offenders(dept_id: str, start: str = Query(...), end: str = Query(...), limit: int = 10):
    return score_svc.get_top_offenders(dept_id, _dr(start, end), limit)


@scorecard_router.get("/department/{dept_id}/trend")
def dept_trend(dept_id: str, start: str = Query(...), end: str = Query(...)):
    return score_svc.get_trend_analysis(dept_id, _dr(start, end))


@scorecard_router.get("/department/{dept_id}/risk-distribution")
def risk_dist(dept_id: str, start: str = Query(...), end: str = Query(...)):
    return score_svc.get_risk_category_distribution(dept_id, _dr(start, end))


@scorecard_router.get("/company")
def company_scorecard(start: str = Query(...), end: str = Query(...)):
    return score_svc.get_company_wide_scorecard(_dr(start, end))


@scorecard_router.get("/compare")
def compare(dept_ids: str = Query(..., description="Comma-separated"), start: str = Query(...), end: str = Query(...)):
    ids = [d.strip() for d in dept_ids.split(",")]
    return score_svc.compare_departments(ids, _dr(start, end))


@scorecard_router.get("/shadow-impact")
def shadow_impact(start: str = Query(...), end: str = Query(...)):
    return score_svc.get_shadow_mode_impact_report(_dr(start, end))


@scorecard_router.get("/training-correlation/{dept_id}")
def training_corr(dept_id: str, start: str = Query(...), end: str = Query(...)):
    return score_svc.get_training_correlation_report(dept_id, _dr(start, end))


@scorecard_router.get("/executive-briefing")
def exec_briefing(start: str = Query(...), end: str = Query(...)):
    return score_svc.generate_executive_briefing(_dr(start, end))


# ═══════════════════════════════════════════════════════════════════════════
#  6. SUPERVISOR DATA ACCESS CONTROL
# ═══════════════════════════════════════════════════════════════════════════

supervisor_router = APIRouter(prefix="/api/supervisor", tags=["Supervisor Access"])


@supervisor_router.post("/request-detail")
def request_detail(req: DetailRequest):
    return sup_svc.handle_detail_request(req)


@supervisor_router.get("/access-policy")
def access_policy(manager_id: str = Query(...), incident_id: str = Query(...)):
    return sup_svc.evaluate_detail_access_policy(manager_id, incident_id)

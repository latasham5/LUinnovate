"""
models.py
Pydantic models shared across all Watchtower services.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────

class SeverityColor(str, Enum):
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class DeploymentMode(str, Enum):
    LIVE = "live"
    SHADOW = "shadow"


class PolicyMode(str, Enum):
    BLOCK = "block"
    WARN = "warn"
    LOG_ONLY = "log_only"


class ActionTaken(str, Enum):
    ALLOWED = "allowed"
    WARNED = "warned"
    BLOCKED = "blocked"
    REDACTED = "redacted"


class NotificationChannel(str, Enum):
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"


class ExportFormat(str, Enum):
    CSV = "csv"
    PDF = "pdf"
    JSON = "json"


# ── Core Records ─────────────────────────────────────────────────────────

class FullFlagRecord(BaseModel):
    incident_id: Optional[str] = None
    timestamp: datetime
    user_id: str
    department_id: str
    risk_category: str
    action_taken: ActionTaken
    policy_version: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    severity_color: SeverityColor
    deployment_mode: DeploymentMode
    policy_mode: PolicyMode
    raw_prompt: Optional[str] = None
    summary: Optional[str] = None


class UserSession(BaseModel):
    user_id: str
    session_start: datetime
    session_end: datetime
    total_prompts: int
    flagged_prompts: int


class ShadowModeEvent(BaseModel):
    user_id: str
    raw_prompt: str
    what_would_have_happened: str
    timestamp: datetime


# ── Alerting ─────────────────────────────────────────────────────────────

class IncidentReport(BaseModel):
    incident_id: Optional[str] = None
    user_id: str
    prompt_summary: Optional[str] = None
    risk_category: str
    action_taken: ActionTaken
    policy_version: str
    confidence_score: float
    timestamp: datetime
    severity_color: SeverityColor


class ManagerAlert(BaseModel):
    manager_id: str
    incident_summary: str
    timestamp: datetime


class CybersecurityAlert(BaseModel):
    team_id: str
    incident_details: dict
    severity: SeverityColor
    timestamp: datetime


class NotificationPayload(BaseModel):
    recipient_id: str
    channel: NotificationChannel
    message: str


# ── User Flag History ────────────────────────────────────────────────────

class FlagEvent(BaseModel):
    user_id: str
    risk_category: str
    severity: SeverityColor
    timestamp: datetime


class ThresholdConfig(BaseModel):
    max_flags_per_period: int = 5
    period_days: int = 30
    training_trigger: bool = True
    supervisor_notify: bool = True


class FlagCountReset(BaseModel):
    user_id: str
    reason: str
    admin_id: str


# ── Micro-Training ──────────────────────────────────────────────────────

class TrainingAssignment(BaseModel):
    user_id: str
    module_id: str
    reason: str
    assigned_timestamp: datetime


class QuizResponse(BaseModel):
    user_id: str
    module_id: str
    question_id: str
    selected_answer: str
    is_correct: bool


class TrainingCompletion(BaseModel):
    user_id: str
    module_id: str
    score: float
    completion_timestamp: datetime


# ── Scorecard ────────────────────────────────────────────────────────────

class DepartmentScore(BaseModel):
    department_id: str
    score: float
    color: SeverityColor
    total_events: int
    date_range_start: datetime
    date_range_end: datetime


class DateRangeParams(BaseModel):
    start: datetime
    end: datetime


# ── Supervisor Access ────────────────────────────────────────────────────

class DetailRequest(BaseModel):
    manager_id: str
    incident_id: str
    justification: str


class DetailAccessLog(BaseModel):
    manager_id: str
    incident_id: str
    timestamp: datetime
    approved_fields: list[str]

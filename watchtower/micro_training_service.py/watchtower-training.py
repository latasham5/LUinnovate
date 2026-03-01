"""
micro_training_service.py
Micro-Training Service — assigns, delivers, and evaluates scenario-based
training modules triggered by flag thresholds.
"""

import json, uuid
from datetime import datetime
from pathlib import Path
from config import supabase, TRAINING_CONTENT_PATH
from models import (
    TrainingAssignment, QuizResponse, TrainingCompletion,
    NotificationPayload, NotificationChannel, DateRangeParams,
)


ASSIGNMENT_TABLE = "training_assignments"
QUIZ_TABLE = "quiz_responses"
COMPLETION_TABLE = "training_completions"

PASS_THRESHOLD = 0.7  # 70 % to pass


# ── Content Loader ───────────────────────────────────────────────────────

def _load_modules() -> dict:
    """Load training module content from local JSON."""
    path = Path(TRAINING_CONTENT_PATH)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def get_training_module_content(module_id: str) -> dict | None:
    modules = _load_modules()
    return modules.get(module_id)


def select_module_by_category(risk_categories: list[str]) -> str:
    """
    Pick the best module based on flagged categories.
    Falls back to a general module if no match.
    """
    modules = _load_modules()
    for mid, mod in modules.items():
        mod_cats = set(mod.get("categories", []))
        if mod_cats & set(risk_categories):
            return mid
    return "general_awareness"  # default fallback


# ── Assignment ───────────────────────────────────────────────────────────

def assign_training_module(
    user_id: str, module_id: str, reason: str
) -> dict:
    data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "module_id": module_id,
        "reason": reason,
        "assigned_timestamp": datetime.utcnow().isoformat(),
        "status": "pending",
    }
    supabase.table(ASSIGNMENT_TABLE).insert(data).execute()
    return data


# ── Quiz Flow ────────────────────────────────────────────────────────────

def record_quiz_response(resp: QuizResponse) -> dict:
    data = resp.model_dump(mode="json")
    data["id"] = str(uuid.uuid4())
    supabase.table(QUIZ_TABLE).insert(data).execute()
    return data


def evaluate_quiz_completion(
    user_id: str, module_id: str, responses: list[QuizResponse]
) -> dict:
    """Determine pass/fail based on correct-answer ratio."""
    total = len(responses)
    correct = sum(1 for r in responses if r.is_correct)
    score = correct / total if total else 0.0
    passed = score >= PASS_THRESHOLD

    result = {
        "user_id": user_id,
        "module_id": module_id,
        "total_questions": total,
        "correct_answers": correct,
        "score": round(score, 2),
        "passed": passed,
    }

    if passed:
        now = datetime.utcnow()
        issue_completion_badge(user_id, module_id, now)
        log_training_completion(TrainingCompletion(
            user_id=user_id,
            module_id=module_id,
            score=score,
            completion_timestamp=now,
        ))
        # Mark assignment complete
        supabase.table(ASSIGNMENT_TABLE).update(
            {"status": "completed"}
        ).eq("user_id", user_id).eq("module_id", module_id).execute()

    return result


# ── Completion & Badges ──────────────────────────────────────────────────

def issue_completion_badge(
    user_id: str, module_id: str, completion_ts: datetime
) -> dict:
    badge = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "module_id": module_id,
        "badge_type": "completion",
        "issued_at": completion_ts.isoformat(),
    }
    supabase.table("training_badges").insert(badge).execute()
    return badge


def log_training_completion(comp: TrainingCompletion) -> dict:
    data = comp.model_dump(mode="json")
    data["id"] = str(uuid.uuid4())
    supabase.table(COMPLETION_TABLE).insert(data).execute()
    return data


# ── Reminders ────────────────────────────────────────────────────────────

def send_training_reminder(
    user_id: str, module_id: str, days_overdue: int
) -> dict:
    from alerting_service import send_notification

    return send_notification(NotificationPayload(
        recipient_id=user_id,
        channel=NotificationChannel.SLACK,
        message=(
            f"[Training Reminder] Module '{module_id}' is {days_overdue} day(s) "
            f"overdue. Please complete it at your earliest convenience."
        ),
    ))


# ── History & Reporting ──────────────────────────────────────────────────

def get_training_history(user_id: str) -> list[dict]:
    """All completed and pending modules for a user."""
    res = (
        supabase.table(ASSIGNMENT_TABLE)
        .select("*, training_completions(*)")
        .eq("user_id", user_id)
        .order("assigned_timestamp", desc=True)
        .execute()
    )
    return res.data


def generate_training_effectiveness_report(
    module_id: str, date_range: DateRangeParams
) -> dict:
    """
    Do completions reduce flags?
    Compares flag rates before and after training completion.
    """
    completions = (
        supabase.table(COMPLETION_TABLE)
        .select("*")
        .eq("module_id", module_id)
        .gte("completion_timestamp", date_range.start.isoformat())
        .lte("completion_timestamp", date_range.end.isoformat())
        .execute()
        .data
    )
    return {
        "module_id": module_id,
        "completions_in_period": len(completions),
        "avg_score": (
            round(sum(c["score"] for c in completions) / len(completions), 2)
            if completions else 0
        ),
        "note": "Cross-reference with flag_events for before/after analysis.",
    }

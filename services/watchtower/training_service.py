"""
Micro-Training Service.

assignTrainingModule, getTrainingModuleContent, selectModuleByCategory,
recordQuizResponse, evaluateQuizCompletion, issueCompletionBadge,
logTrainingCompletion, sendTrainingReminder, getTrainingHistory,
generateTrainingEffectivenessReport.

Uses in-memory stores for development. Training module content is loaded
from data/training_modules/*.json files on disk.
"""

import json
import os
import uuid
from collections import defaultdict
from typing import Optional
from datetime import datetime

from services.watchtower.logging_service import _prompt_events

# Path to training modules
TRAINING_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "training_modules")

# ---------------------------------------------------------------------------
# In-memory stores (replace with Supabase in production)
# ---------------------------------------------------------------------------
_training_assignments: list[dict] = []   # {user_id, module_id, reason, assigned_timestamp, status}
_quiz_responses: list[dict] = []         # {user_id, module_id, question_id, selected_answer, is_correct, timestamp}
_training_completions: list[dict] = []   # {user_id, module_id, score, completion_timestamp}
_badges: list[dict] = []                 # {user_id, module_id, badge_id, awarded_at}
_training_reminders: list[dict] = []     # {user_id, module_id, days_overdue, sent_at}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def assign_training_module(user_id: str, module_id: str, reason: str, assigned_timestamp: str) -> None:
    """Create a training assignment for a user."""
    # Avoid duplicate active assignments for the same module
    existing = [
        a for a in _training_assignments
        if a["user_id"] == user_id and a["module_id"] == module_id and a["status"] == "pending"
    ]
    if existing:
        return  # already assigned

    _training_assignments.append({
        "assignment_id": f"ASSIGN_{uuid.uuid4().hex[:10]}",
        "user_id": user_id,
        "module_id": module_id,
        "reason": reason,
        "assigned_timestamp": assigned_timestamp,
        "status": "pending",  # pending, in_progress, completed
    })


def get_training_module_content(module_id: str) -> dict:
    """Retrieve scenario-based training content from local JSON."""
    filepath = os.path.join(TRAINING_DIR, f"{module_id}.json")
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"module_id": module_id, "error": "Module not found"}


def select_module_by_category(risk_categories: list[str]) -> str:
    """Pick the right training module based on flagged categories."""
    # Map risk categories to training modules
    category_to_module = {
        "PII": "pii_training",
        "CREDENTIALS": "credentials_training",
        "FINANCIAL": "financial_training",
        "CUSTOMER_INFO": "pii_training",
        "PROPRIETARY": "credentials_training",
        "INTERNAL_CODE_NAME": "credentials_training",
        "REGULATED": "financial_training",
    }

    # Return the module for the highest-priority category
    for cat in risk_categories:
        if cat in category_to_module:
            return category_to_module[cat]

    return "pii_training"  # Default module


async def record_quiz_response(
    user_id: str,
    module_id: str,
    question_id: str,
    selected_answer: str,
    is_correct: bool,
) -> None:
    """Log each quiz answer."""
    _quiz_responses.append({
        "response_id": f"RESP_{uuid.uuid4().hex[:10]}",
        "user_id": user_id,
        "module_id": module_id,
        "question_id": question_id,
        "selected_answer": selected_answer,
        "is_correct": is_correct,
        "timestamp": datetime.utcnow().isoformat(),
    })


async def evaluate_quiz_completion(user_id: str, module_id: str, responses: list[dict]) -> dict:
    """Determine pass/fail based on quiz responses."""
    if not responses:
        return {"passed": False, "score": 0, "total": 0}

    correct = sum(1 for r in responses if r.get("is_correct", False))
    total = len(responses)
    score = (correct / total) * 100 if total > 0 else 0
    passed = score >= 70  # 70% passing threshold

    result = {"passed": passed, "score": score, "correct": correct, "total": total}

    # If passed, auto-complete the training
    if passed:
        now = datetime.utcnow().isoformat()
        await log_training_completion(user_id, module_id, score, now)
        await issue_completion_badge(user_id, module_id, now)

    return result


async def issue_completion_badge(user_id: str, module_id: str, completion_timestamp: str) -> None:
    """Grant a badge for completing a training module."""
    badge = {
        "badge_id": f"BADGE_{uuid.uuid4().hex[:10]}",
        "user_id": user_id,
        "module_id": module_id,
        "awarded_at": completion_timestamp,
    }
    _badges.append(badge)


async def log_training_completion(
    user_id: str,
    module_id: str,
    score: float,
    completion_timestamp: str,
) -> None:
    """Create audit record for training completion and update assignment status."""
    _training_completions.append({
        "user_id": user_id,
        "module_id": module_id,
        "score": score,
        "completion_timestamp": completion_timestamp,
    })

    # Update assignment status
    for assignment in _training_assignments:
        if (
            assignment["user_id"] == user_id
            and assignment["module_id"] == module_id
            and assignment["status"] in ("pending", "in_progress")
        ):
            assignment["status"] = "completed"


async def send_training_reminder(user_id: str, module_id: str, days_overdue: int) -> None:
    """Send nudge notification if training is overdue.

    Dev mode: logs to _training_reminders and dispatches via alerting_service.
    """
    from services.watchtower.alerting_service import send_notification

    _training_reminders.append({
        "user_id": user_id,
        "module_id": module_id,
        "days_overdue": days_overdue,
        "sent_at": datetime.utcnow().isoformat(),
    })

    message = (
        f"Reminder: Your training module '{module_id}' is {days_overdue} day(s) overdue. "
        f"Please complete it at your earliest convenience."
    )
    await send_notification(
        recipient_id=user_id,
        channel="slack",
        message=message,
    )


async def get_training_history(user_id: str) -> dict:
    """All completed and pending training modules for a user."""
    user_assignments = [a for a in _training_assignments if a["user_id"] == user_id]
    user_completions = [c for c in _training_completions if c["user_id"] == user_id]
    completed_module_ids = {c["module_id"] for c in user_completions}

    completed = [
        {
            "module_id": c["module_id"],
            "score": c["score"],
            "completion_timestamp": c["completion_timestamp"],
        }
        for c in user_completions
    ]

    pending = [
        {
            "module_id": a["module_id"],
            "assigned_timestamp": a["assigned_timestamp"],
            "reason": a["reason"],
        }
        for a in user_assignments
        if a["status"] == "pending" and a["module_id"] not in completed_module_ids
    ]

    # Overdue: pending assignments older than 7 days
    now = datetime.utcnow()
    overdue = []
    for a in user_assignments:
        if a["status"] == "pending" and a["module_id"] not in completed_module_ids:
            try:
                assigned_dt = datetime.fromisoformat(a["assigned_timestamp"])
                if (now - assigned_dt).days > 7:
                    overdue.append({
                        "module_id": a["module_id"],
                        "assigned_timestamp": a["assigned_timestamp"],
                        "days_overdue": (now - assigned_dt).days,
                    })
            except (ValueError, TypeError):
                pass

    return {"completed": completed, "pending": pending, "overdue": overdue}


async def generate_training_effectiveness_report(
    module_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Analyze whether training completions reduce flags.

    For each user who completed the module, compare their flag rate before
    and after completion.
    """
    # Get all completions for this module
    completions = [c for c in _training_completions if c["module_id"] == module_id]
    if date_from:
        completions = [c for c in completions if c.get("completion_timestamp", "") >= date_from]
    if date_to:
        completions = [c for c in completions if c.get("completion_timestamp", "") <= date_to]

    if not completions:
        return {
            "module_id": module_id,
            "completions": 0,
            "avg_flag_reduction_percent": 0.0,
            "effective": False,
        }

    reduction_pcts = []
    for comp in completions:
        uid = comp["user_id"]
        comp_ts = comp.get("completion_timestamp", "")

        # Count flags before and after training completion
        user_events = [
            e for e in _prompt_events
            if e.get("user_id") == uid and e.get("action_taken") != "ALLOWED"
        ]
        before = len([e for e in user_events if e.get("created_at", "") < comp_ts])
        after = len([e for e in user_events if e.get("created_at", "") >= comp_ts])

        if before > 0:
            reduction = ((before - after) / before) * 100
            reduction_pcts.append(reduction)

    avg_reduction = round(sum(reduction_pcts) / len(reduction_pcts), 2) if reduction_pcts else 0.0

    return {
        "module_id": module_id,
        "completions": len(completions),
        "avg_flag_reduction_percent": avg_reduction,
        "effective": avg_reduction > 20,  # >20% reduction is considered effective
    }

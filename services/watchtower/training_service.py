"""
Micro-Training Service.

assignTrainingModule, getTrainingModuleContent, selectModuleByCategory,
recordQuizResponse, evaluateQuizCompletion, issueCompletionBadge,
logTrainingCompletion, sendTrainingReminder, getTrainingHistory,
generateTrainingEffectivenessReport.
"""

import json
import os
from typing import Optional
from datetime import datetime

# Path to training modules
TRAINING_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "training_modules")


async def assign_training_module(user_id: str, module_id: str, reason: str, assigned_timestamp: str) -> None:
    """Create a training assignment for a user."""
    # TODO: Insert into Supabase 'training_assignments' table
    pass


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
    # TODO: Insert into Supabase 'quiz_responses' table
    pass


async def evaluate_quiz_completion(user_id: str, module_id: str, responses: list[dict]) -> dict:
    """Determine pass/fail based on quiz responses."""
    if not responses:
        return {"passed": False, "score": 0, "total": 0}

    correct = sum(1 for r in responses if r.get("is_correct", False))
    total = len(responses)
    score = (correct / total) * 100 if total > 0 else 0
    passed = score >= 70  # 70% passing threshold

    return {"passed": passed, "score": score, "correct": correct, "total": total}


async def issue_completion_badge(user_id: str, module_id: str, completion_timestamp: str) -> None:
    """Grant a badge for completing a training module."""
    # TODO: Insert into Supabase 'badges' table
    pass


async def log_training_completion(
    user_id: str,
    module_id: str,
    score: float,
    completion_timestamp: str,
) -> None:
    """Create audit record for training completion."""
    # TODO: Insert into Supabase 'training_completions' table
    pass


async def send_training_reminder(user_id: str, module_id: str, days_overdue: int) -> None:
    """Send nudge notification if training is overdue."""
    # TODO: Call alerting_service.send_notification
    pass


async def get_training_history(user_id: str) -> dict:
    """All completed and pending training modules for a user."""
    # TODO: Query Supabase for user's training records
    return {"completed": [], "pending": [], "overdue": []}


async def generate_training_effectiveness_report(
    module_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Analyze whether training completions reduce flags."""
    # TODO: Correlate training completions with subsequent flag rates
    return {
        "module_id": module_id,
        "completions": 0,
        "avg_flag_reduction_percent": 0.0,
        "effective": False,
    }

"""
Micro-training routes — training modules, quizzes, completion tracking.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.watchtower.training_service import (
    get_training_module_content as _get_training_module_content,
    get_training_history as _get_training_history,
    record_quiz_response as _record_quiz_response,
    evaluate_quiz_completion as _evaluate_quiz_completion,
    generate_training_effectiveness_report as _generate_training_effectiveness_report,
)

router = APIRouter()


class QuizResponseRequest(BaseModel):
    """User's answer to a quiz question."""
    user_id: str
    module_id: str
    question_id: str
    selected_answer: str


@router.get("/modules/{module_id}")
async def get_training_module(module_id: str):
    """Retrieve scenario-based training content."""
    content = _get_training_module_content(module_id)
    return {"module_id": module_id, "content": content}


@router.get("/user/{user_id}/history")
async def get_training_history(user_id: str):
    """All completed and pending training modules for a user."""
    history = await _get_training_history(user_id)
    return {
        "user_id": user_id,
        "completed": history.get("completed", []),
        "pending": history.get("pending", []),
    }


@router.post("/quiz/submit")
async def submit_quiz_response(request: QuizResponseRequest):
    """Log a quiz answer."""
    # Load the module to check the correct answer
    module = _get_training_module_content(request.module_id)
    is_correct = False
    quiz = module.get("quiz", [])
    for question in quiz:
        if question.get("question_id") == request.question_id:
            is_correct = request.selected_answer == question.get("correct_answer", "")
            break

    await _record_quiz_response(
        user_id=request.user_id,
        module_id=request.module_id,
        question_id=request.question_id,
        selected_answer=request.selected_answer,
        is_correct=is_correct,
    )
    return {"recorded": True, "is_correct": is_correct}


@router.get("/quiz/evaluate/{user_id}/{module_id}")
async def evaluate_quiz(user_id: str, module_id: str):
    """Determine pass/fail for a completed quiz."""
    result = await _evaluate_quiz_completion(user_id, module_id, [])
    return {
        "user_id": user_id,
        "module_id": module_id,
        "passed": result.get("passed", False),
        "score": result.get("score", 0),
    }


@router.get("/effectiveness/{module_id}")
async def get_training_effectiveness(module_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None):
    """Do training completions reduce flags?"""
    report = await _generate_training_effectiveness_report(module_id, date_from, date_to)
    return {"module_id": module_id, "effectiveness": report}

"""
Micro-training routes — training modules, quizzes, completion tracking.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

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
    # TODO: watchtower.training_service.getTrainingModuleContent
    return {"module_id": module_id, "content": {}}


@router.get("/user/{user_id}/history")
async def get_training_history(user_id: str):
    """All completed and pending training modules for a user."""
    # TODO: watchtower.training_service.getTrainingHistory
    return {"user_id": user_id, "completed": [], "pending": []}


@router.post("/quiz/submit")
async def submit_quiz_response(request: QuizResponseRequest):
    """Log a quiz answer."""
    # TODO: watchtower.training_service.recordQuizResponse
    return {"recorded": True}


@router.get("/quiz/evaluate/{user_id}/{module_id}")
async def evaluate_quiz(user_id: str, module_id: str):
    """Determine pass/fail for a completed quiz."""
    # TODO: watchtower.training_service.evaluateQuizCompletion
    return {"user_id": user_id, "module_id": module_id, "passed": False, "score": 0}


@router.get("/effectiveness/{module_id}")
async def get_training_effectiveness(module_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None):
    """Do training completions reduce flags?"""
    # TODO: watchtower.training_service.generateTrainingEffectivenessReport
    return {"module_id": module_id, "effectiveness": {}}

"""
Prompt routes — the main entry point for the entire platform.
POST /prompt receives every user prompt from the frontend.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from api.dependencies import get_current_user
from services.enforcer.auth_service import get_user_profile
from services.enforcer.policy_service import build_policy_context
from services.enforcer.action_executor import execute_action
from services.gatekeeper.prompt_receiver import receive_prompt as gatekeeper_receive
from shared.enums import ActionType, RiskCategory

router = APIRouter()


class PromptRequest(BaseModel):
    """Incoming prompt from the frontend."""
    raw_prompt: str
    policy_mode: Optional[str] = "BALANCED"  # STRICT, BALANCED, FAST


class PromptResponse(BaseModel):
    """Response sent back to the frontend."""
    action: str
    response_content: Optional[str] = None
    rewritten_prompt: Optional[str] = None
    rewrite_explanation: Optional[list[str]] = None
    severity_color: Optional[str] = None
    warning_message: Optional[str] = None
    disclaimers: list[str] = []


@router.post("/", response_model=PromptResponse)
async def handle_prompt(request: PromptRequest, user: dict = Depends(get_current_user)):
    """
    Main entry point — receives a prompt and runs it through the full pipeline:
    1. Developer 2 provides PolicyContext (auth, policies, thresholds)
    2. Developer 1 analyzes, scores, and optionally rewrites the prompt
    3. Developer 2 executes the action (forward to CokeGPT or block)
    4. Developer 3 logs everything
    """
    employee_id = user.get("employee_id", "EMP001")

    # Step 1: Get user profile
    user_profile = get_user_profile(employee_id)

    # Step 2: Build policy context
    policy_context = build_policy_context(user_profile, request.policy_mode)

    # Step 3: Run Gatekeeper analysis pipeline
    analysis = await gatekeeper_receive(
        user_id=employee_id,
        raw_prompt=request.raw_prompt,
        timestamp=datetime.utcnow().isoformat(),
        policy_context=policy_context,
        user_history=None,
    )

    # Override: Credentials are ALWAYS blocked, even in shadow mode
    if RiskCategory.CREDENTIALS in analysis.detected_categories:
        analysis.recommended_action = ActionType.BLOCKED

    # Step 4: Execute action (forward to CokeGPT, block, or rewrite)
    result = await execute_action(
        user_id=employee_id,
        raw_prompt=request.raw_prompt,
        analysis=analysis,
    )

    # Step 5: Log the event (async, non-blocking)
    try:
        from services.watchtower.logging_service import log_prompt_event
        await log_prompt_event(
            user_id=employee_id,
            department_id=user_profile.department_id,
            raw_prompt=request.raw_prompt,
            analysis=analysis,
            policy_context=policy_context,
        )
    except Exception:
        pass  # Logging failure should not break the response

    return PromptResponse(
        action=result.get("action", "ALLOWED"),
        response_content=result.get("response_content"),
        rewritten_prompt=result.get("rewritten_prompt"),
        rewrite_explanation=result.get("rewrite_explanation"),
        severity_color=result.get("severity_color"),
        warning_message=result.get("warning_message"),
        disclaimers=result.get("disclaimers", []),
    )

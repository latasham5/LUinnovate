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
    detected_categories: list[str] = []
    risk_score: float = 0.0
    explanation: str = ""
    detected_details: list[dict] = []


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

    # Build detailed explanation of ALL findings
    all_categories = [c.value for c in analysis.detected_categories]
    detected_details = []
    for element in analysis.detected_elements:
        detected_details.append({
            "text": element.text[:50] + "..." if len(element.text) > 50 else element.text,
            "category": element.category.value,
            "confidence": round(element.confidence, 2),
        })

    # Build human-readable explanation listing ALL issues
    explanation_parts = []
    category_counts: dict[str, int] = {}
    for element in analysis.detected_elements:
        cat = element.category.value
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in category_counts.items():
        explanation_parts.append(f"{count} {cat} detection{'s' if count > 1 else ''}")

    explanation = f"Found: {', '.join(explanation_parts)}." if explanation_parts else "No issues detected."
    explanation += f" Risk score: {analysis.risk_score:.0f}/100. Action: {result.get('action', 'ALLOWED')}."

    return PromptResponse(
        action=result.get("action", "ALLOWED"),
        response_content=result.get("response_content"),
        rewritten_prompt=result.get("rewritten_prompt") or analysis.rewritten_prompt,
        rewrite_explanation=result.get("rewrite_explanation") or analysis.rewrite_explanation,
        severity_color=result.get("severity_color") or (analysis.severity_color.value if analysis.severity_color else None),
        warning_message=result.get("warning_message"),
        disclaimers=result.get("disclaimers", []),
        detected_categories=all_categories,
        risk_score=analysis.risk_score,
        explanation=explanation,
        detected_details=detected_details,
    )

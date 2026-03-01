"""
Prompt routes — the main entry point for the entire platform.
POST /prompt receives every user prompt from the frontend.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from api.dependencies import get_current_user

router = APIRouter()


class PromptRequest(BaseModel):
    """Incoming prompt from the frontend."""
    raw_prompt: str
    policy_mode: Optional[str] = "BALANCED"  # STRICT, BALANCED, FAST


class PromptResponse(BaseModel):
    """Response sent back to the frontend."""
    action: str  # ALLOWED, ALLOWED_WITH_WARNING, REWRITTEN, BLOCKED, SHADOW_LOGGED
    response_content: Optional[str] = None
    rewritten_prompt: Optional[str] = None
    rewrite_explanation: Optional[list[str]] = None
    severity_color: Optional[str] = None
    warning_message: Optional[str] = None
    disclaimers: list[str] = []


@router.post("/", response_model=PromptResponse)
async def receive_prompt(request: PromptRequest, user: dict = Depends(get_current_user)):
    """
    Main entry point — receives a prompt and runs it through the full pipeline:
    1. Developer 2 provides PolicyContext (auth, policies, thresholds)
    2. Developer 1 analyzes, scores, and optionally rewrites the prompt
    3. Developer 2 executes the action (forward to CokeGPT or block)
    4. Developer 3 logs everything
    """
    # TODO: Wire up the full pipeline
    # Step 1: enforcer.auth_service.validateSSOToken + getUserProfile
    # Step 2: enforcer.policy_service.build PolicyContext
    # Step 3: gatekeeper.prompt_receiver.receivePrompt
    # Step 4: enforcer.action_executor.execute based on AnalysisResult
    # Step 5: watchtower.logging_service.logPromptEvent

    return PromptResponse(
        action="ALLOWED",
        response_content="Pipeline not yet wired — prompt received successfully.",
        disclaimers=["This is a development placeholder response."],
    )

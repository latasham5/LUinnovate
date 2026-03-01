"""
Action Execution Service — executes what Developer 1 decides.

blockPrompt, forwardToGPT, receiveGPTResponse,
scanGPTResponse, returnResponseToUser, executeShadowMode.
"""

from typing import Optional
from shared.schemas.analysis_result import AnalysisResult
from shared.enums import ActionType
from shared.exceptions import PromptBlockedError, CokeGPTError
from services.enforcer.cokegpt_client import send_to_cokegpt


async def execute_action(
    user_id: str,
    raw_prompt: str,
    analysis: AnalysisResult,
) -> dict:
    """
    Execute the action determined by the Gatekeeper.
    Returns the response to send back to the frontend.
    """
    action = analysis.recommended_action

    if action == ActionType.BLOCKED:
        result = block_prompt(
            user_id=user_id,
            raw_prompt=raw_prompt,
            reason=f"Blocked due to {', '.join(c.value for c in analysis.detected_categories)}",
            policy_version="1.0.0",
        )
        # Include rewrite info even for blocked prompts so frontend can show ALL findings
        result["rewritten_prompt"] = analysis.rewritten_prompt
        result["rewrite_explanation"] = analysis.rewrite_explanation
        result["severity_color"] = analysis.severity_color.value if analysis.severity_color else "RED"
        return result

    elif action == ActionType.REWRITTEN:
        # Forward the rewritten prompt to CokeGPT
        prompt_to_send = analysis.rewritten_prompt or raw_prompt
        response = await forward_to_gpt(prompt_to_send, user_id)
        return {
            "action": ActionType.REWRITTEN.value,
            "response_content": response,
            "rewritten_prompt": analysis.rewritten_prompt,
            "rewrite_explanation": analysis.rewrite_explanation,
            "severity_color": analysis.severity_color.value,
            "warning_message": "Your prompt was modified for safety. See explanation below.",
            "disclaimers": ["This response was generated from a sanitized version of your prompt."],
        }

    elif action == ActionType.ALLOWED_WITH_WARNING:
        response = await forward_to_gpt(raw_prompt, user_id)
        return {
            "action": ActionType.ALLOWED_WITH_WARNING.value,
            "response_content": response,
            "severity_color": analysis.severity_color.value,
            "warning_message": "Your prompt contained potentially sensitive content. Please review.",
            "disclaimers": [],
        }

    elif action == ActionType.SHADOW_LOGGED:
        # In shadow mode: forward original prompt but log what would have happened
        response = await forward_to_gpt(raw_prompt, user_id)
        return {
            "action": ActionType.SHADOW_LOGGED.value,
            "response_content": response,
            "severity_color": analysis.severity_color.value,
            "disclaimers": [],
        }

    else:
        # ALLOWED — forward as-is
        response = await forward_to_gpt(raw_prompt, user_id)
        return {
            "action": ActionType.ALLOWED.value,
            "response_content": response,
            "disclaimers": [],
        }


def block_prompt(user_id: str, raw_prompt: str, reason: str, policy_version: str) -> dict:
    """Hard stop — generates denial record."""
    return {
        "action": ActionType.BLOCKED.value,
        "response_content": None,
        "warning_message": f"Your prompt has been blocked: {reason}",
        "severity_color": "RED",
        "disclaimers": [f"Policy version: {policy_version}"],
    }


async def forward_to_gpt(sanitized_prompt: str, user_id: str) -> str:
    """Send approved or rewritten prompt to CokeGPT."""
    response = await send_to_cokegpt(sanitized_prompt, user_id)
    return response


def scan_gpt_response(response_content: str) -> dict:
    """
    Call Developer 1's detection functions on the GPT response
    to catch sensitive data in the output.
    """
    # TODO: Run detectors on response_content
    # TODO: If sensitive data found, sanitize before returning
    return {"clean": True, "content": response_content}


def return_response_to_user(user_id: str, response_content: str, disclaimers: list[str]) -> dict:
    """Deliver the clean response back to the frontend."""
    return {
        "user_id": user_id,
        "response": response_content,
        "disclaimers": disclaimers,
    }

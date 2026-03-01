"""
Action Execution Service
Developer 2 - The Enforcer
Executes what Developer 1's risk engine decides.
"""
import uuid
from datetime import datetime

# Placeholder for CokeGPT API key (would be env var in production)
COKEGPT_API_KEY = "MOCK-COKEGPT-KEY-PLACEHOLDER"
COKEGPT_ENDPOINT = "https://internal.coke.ai/v1/chat"

# In-memory logs for actions taken
_action_log = []
_shadow_log = []


def _log_action(action_type: str, details: dict):
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "action": action_type,
        **details
    }
    _action_log.append(entry)
    return entry


def block_prompt(user_id: str, raw_prompt: str, reason: str, policy_version: str) -> dict:
    """Hard stop — generates denial record."""
    record = _log_action("BLOCK", {
        "user_id": user_id,
        "prompt_snippet": raw_prompt[:100],
        "reason": reason,
        "policy_version": policy_version
    })
    return {
        "blocked": True,
        "record_id": record["id"],
        "message": f"Prompt blocked: {reason}"
    }


def forward_to_gpt(sanitized_prompt: str, user_id: str) -> dict:
    """Send approved/rewritten prompt to CokeGPT via internal API."""
    # MOCK — in production this hits COKEGPT_ENDPOINT with COKEGPT_API_KEY
    _log_action("FORWARD", {
        "user_id": user_id,
        "prompt_length": len(sanitized_prompt)
    })
    # Simulated response
    mock_response = f"[MOCK CokeGPT Response] Processed prompt ({len(sanitized_prompt)} chars) for user {user_id}."
    return {
        "success": True,
        "response_content": mock_response,
        "model": "cokegpt-internal-v2"
    }


def receive_gpt_response(response_content: str) -> dict:
    """Capture CokeGPT's raw output."""
    return {
        "received": True,
        "content_length": len(response_content),
        "content": response_content,
        "timestamp": datetime.utcnow().isoformat()
    }


def scan_gpt_response(response_content: str) -> dict:
    """
    Call Developer 1's detection functions on the response
    to catch sensitive data in CokeGPT output.
    Stub — will import from dev1's detection module.
    """
    # Placeholder: check for obvious patterns
    flags = []
    sensitive_keywords = ["password", "ssn", "secret_formula", "api_key"]
    for kw in sensitive_keywords:
        if kw.lower() in response_content.lower():
            flags.append(kw)
    return {
        "clean": len(flags) == 0,
        "flags": flags,
        "scanned_length": len(response_content)
    }


def return_response_to_user(user_id: str, response_content: str, disclaimers: list[str] = None) -> dict:
    """Deliver clean response back to frontend."""
    disclaimers = disclaimers or ["AI-generated content. Verify before use."]
    _log_action("RETURN", {
        "user_id": user_id,
        "response_length": len(response_content)
    })
    return {
        "user_id": user_id,
        "content": response_content,
        "disclaimers": disclaimers,
        "delivered": True
    }


def execute_shadow_mode(risk_score: float, risk_category: str) -> dict:
    """
    Shadow mode logic:
    - Always blocks credentials regardless of mode
    - Logs everything else
    - Generates 'what would have happened' records
    - Offers safer rewrite suggestions without enforcing
    """
    hard_block = risk_category == "credentials"

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "risk_score": risk_score,
        "risk_category": risk_category,
        "hard_blocked": hard_block,
        "would_have_blocked": risk_score >= 0.6,
        "would_have_rewritten": 0.3 <= risk_score < 0.6,
        "suggestion": "Consider removing sensitive details" if risk_score >= 0.3 else None
    }
    _shadow_log.append(record)
    return record


def get_action_log() -> list[dict]:
    """Retrieve all action records (for Developer 3 logging)."""
    return _action_log.copy()


def get_shadow_log() -> list[dict]:
    """Retrieve all shadow mode records."""
    return _shadow_log.copy()


if __name__ == "__main__":
    # Smoke tests
    print("=== Block ===")
    print(block_prompt("EMP001", "Here is the root password: hunter2", "credentials_detected", "POL-001:1.0.0"))

    print("\n=== Forward ===")
    result = forward_to_gpt("Summarize Q3 marketing report", "EMP001")
    print(result)

    print("\n=== Receive ===")
    print(receive_gpt_response(result["response_content"]))

    print("\n=== Scan ===")
    print(scan_gpt_response("The results show password resets increased by 40%"))
    print(scan_gpt_response("Revenue grew 12% YoY"))

    print("\n=== Shadow Mode ===")
    print(execute_shadow_mode(0.85, "credentials"))
    print(execute_shadow_mode(0.45, "pii"))
    print(execute_shadow_mode(0.15, "general"))

"""Policy Service - Policy Management"""
from .policy_service import (
    load_policy_document,
    get_active_policies,
    get_policy_by_category,
    map_prompt_to_policy,
    get_policy_version,
    update_policy_rules,
    get_allowed_prompt_templates,
    validate_policy_consistency,
    get_policy_thresholds_by_mode,
    get_micro_training_trigger_threshold,
)
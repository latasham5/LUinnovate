"""
Action Determination — the final decision on what happens to a prompt.

determineAction(): ALLOWED, ALLOWED_WITH_WARNING, REWRITTEN, BLOCKED, or SHADOW_LOGGED.
"""

from shared.enums import ActionType, RiskCategory, SeverityColor, DeploymentMode


def determine_action(
    risk_score: float,
    policy_rules: list,
    policy_mode: str,
    deployment_mode: str,
) -> ActionType:
    """
    The final decision: what happens to this prompt?

    Logic:
    - SHADOW mode: Log everything, block only credentials, suggest rewrites
    - FULL_ENFORCEMENT mode: Apply full policy rules
    - Credentials are ALWAYS blocked regardless of mode
    - Score 0: ALLOWED
    - Score 1-39 (Yellow): ALLOWED_WITH_WARNING
    - Score 40-69 (Orange): REWRITTEN
    - Score 70-100 (Red): BLOCKED
    """
    # Shadow mode overrides
    if deployment_mode == DeploymentMode.SHADOW.value:
        # Credentials are always blocked even in shadow mode
        # (this is checked at a higher level based on detected categories)
        return ActionType.SHADOW_LOGGED

    # Full enforcement logic
    if risk_score == 0:
        return ActionType.ALLOWED
    elif risk_score < 40:
        return ActionType.ALLOWED_WITH_WARNING
    elif risk_score < 70:
        return ActionType.REWRITTEN
    else:
        return ActionType.BLOCKED

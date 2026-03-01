"""
Shadow Mode Management Service.

getDeploymentMode, setDeploymentMode, getShadowModeConfig,
updateShadowModeConfig, generateShadowToEnforcementReadinessReport,
compareShadowVsEnforcement, executeShadowMode.
"""

from shared.enums import ActionType, RiskCategory, SeverityColor
from config.settings import settings


# In-memory shadow mode config (replace with DB in production)
_shadow_config = {
    "hard_block": [RiskCategory.CREDENTIALS.value],  # Always blocked even in shadow mode
    "log_only": [
        RiskCategory.FINANCIAL.value,
        RiskCategory.PII.value,
        RiskCategory.CUSTOMER_INFO.value,
        RiskCategory.PROPRIETARY.value,
        RiskCategory.INTERNAL_CODE_NAME.value,
        RiskCategory.REGULATED.value,
    ],
}


def get_deployment_mode() -> str:
    """Return current deployment mode."""
    return settings.DEPLOYMENT_MODE


def set_deployment_mode(admin_id: str, mode: str, effective_date: str) -> bool:
    """Switch between shadow and full enforcement."""
    # TODO: Validate admin permissions
    # TODO: Schedule mode switch for effective_date
    # TODO: Log the mode change
    return True


def get_shadow_mode_config() -> dict:
    """Return what is logged-only vs hard-blocked in shadow mode."""
    return _shadow_config


def update_shadow_mode_config(admin_id: str, config: dict) -> bool:
    """Adjust shadow mode rules."""
    global _shadow_config
    # TODO: Validate admin permissions
    _shadow_config.update(config)
    return True


def execute_shadow_mode(risk_score: float, risk_category: str) -> dict:
    """
    Shadow mode logic:
    - Always blocks credentials regardless of mode
    - Logs everything else
    - Generates "what would have happened" records
    - Still offers safer rewrite suggestions without enforcing
    """
    # Credentials are always blocked
    if risk_category == RiskCategory.CREDENTIALS.value:
        return {
            "action": ActionType.BLOCKED.value,
            "reason": "Credentials blocked even in shadow mode",
            "shadow_logged": True,
        }

    # Everything else is logged with "what would have happened"
    if risk_score >= 70:
        would_have_been = ActionType.BLOCKED.value
    elif risk_score >= 40:
        would_have_been = ActionType.REWRITTEN.value
    elif risk_score > 0:
        would_have_been = ActionType.ALLOWED_WITH_WARNING.value
    else:
        would_have_been = ActionType.ALLOWED.value

    return {
        "action": ActionType.SHADOW_LOGGED.value,
        "would_have_been": would_have_been,
        "shadow_logged": True,
        "risk_score": risk_score,
    }


def generate_shadow_to_enforcement_readiness_report() -> dict:
    """Analyze shadow data and recommend whether to go live."""
    # TODO: Query Developer 3's database for shadow mode events
    # TODO: Calculate false positive rates
    # TODO: Generate recommendation
    return {
        "ready": False,
        "total_shadow_events": 0,
        "estimated_false_positive_rate": 0.0,
        "recommendation": "Insufficient shadow data. Continue collecting.",
    }


def compare_shadow_vs_enforcement(date_from: str, date_to: str) -> dict:
    """Reports showing what would have been blocked vs what was only logged."""
    # TODO: Query shadow mode logs from Developer 3's database
    return {
        "date_range": {"from": date_from, "to": date_to},
        "total_events": 0,
        "would_have_blocked": 0,
        "would_have_rewritten": 0,
        "would_have_warned": 0,
        "only_logged": 0,
    }

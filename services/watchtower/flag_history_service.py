"""
User Flag History & Threshold Service.

recordFlagEvent, getUserFlagCount, getUserFlagsByCategory,
checkThreshold, triggerMicroTraining, triggerSupervisorNotification,
getUserRiskTrend, resetFlagCount.
"""

from typing import Optional
from shared.schemas.user_history import UserHistory, CategoryBreakdown


async def record_flag_event(user_id: str, risk_category: str, severity: str, timestamp: str) -> None:
    """Add to the user's running flag history."""
    # TODO: Insert into Supabase 'flag_events' table
    pass


async def get_user_flag_count(user_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
    """Total flags in period."""
    # TODO: Query Supabase COUNT where user_id and date range
    return 0


async def get_user_flags_by_category(
    user_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[CategoryBreakdown]:
    """Breakdown by risk category."""
    # TODO: Query Supabase GROUP BY risk_category
    return []


async def check_threshold(user_id: str, flag_count: int, threshold_config: int) -> bool:
    """Evaluate whether training is triggered."""
    return flag_count >= threshold_config


async def trigger_micro_training(user_id: str, relevant_categories: list[str]) -> None:
    """Assign the right training module based on flagged categories."""
    # TODO: Call training_service.assignTrainingModule
    pass


async def trigger_supervisor_notification(user_id: str, manager_id: str, flag_summary: dict) -> None:
    """Notify manager with minimal compliant info."""
    # TODO: Call alerting_service.flag_manager with privacy-safe summary
    pass


async def get_user_risk_trend(user_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> str:
    """Determine if user is improving or worsening over time."""
    # TODO: Query historical flag data and calculate trend
    # Compare recent period vs older period
    return "STABLE"  # IMPROVING, STABLE, WORSENING


async def reset_flag_count(user_id: str, reason: str, admin_id: str) -> bool:
    """Authorized reset after training or review."""
    # TODO: Update Supabase records
    # TODO: Log the reset with reason and admin_id
    return True


async def get_user_history(user_id: str) -> UserHistory:
    """
    Build the complete UserHistory object for Developer 1.
    This is the main interface function.
    """
    flag_count = await get_user_flag_count(user_id)
    category_breakdown = await get_user_flags_by_category(user_id)
    risk_trend = await get_user_risk_trend(user_id)

    return UserHistory(
        user_id=user_id,
        total_flag_count=flag_count,
        flag_count_last_30_days=flag_count,
        category_breakdown=category_breakdown,
        risk_trend=risk_trend,
    )

"""
UserHistory — Developer 3 -> Developer 1 contract.

Contains flag count, category breakdown, risk trend, and training status.
"""

from typing import Optional
from pydantic import BaseModel
from shared.enums import RiskCategory


class CategoryBreakdown(BaseModel):
    """Flag count breakdown by risk category."""
    category: RiskCategory
    count: int


class UserHistory(BaseModel):
    """User's historical behavior data for risk scoring."""

    user_id: str

    # Flag counts
    total_flag_count: int = 0
    flag_count_last_30_days: int = 0
    category_breakdown: list[CategoryBreakdown] = []

    # Risk trend
    risk_trend: str = "STABLE"  # IMPROVING, STABLE, WORSENING

    # Training status
    training_completed: bool = False
    pending_training_modules: list[str] = []
    last_training_date: Optional[str] = None

    # Historical risk score average
    average_risk_score: float = 0.0

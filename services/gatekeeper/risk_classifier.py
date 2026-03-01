"""
Risk Classification Service — scoring, categorization, severity mapping.

classifyRiskCategory, calculateRiskScore, calculateConfidenceScore,
mapRiskToSeverity, evaluateAgainstPolicy, checkUserRiskHistory.
"""

from typing import Optional
from shared.schemas.analysis_result import DetectedElement
from shared.schemas.policy_context import PolicyThresholds
from shared.schemas.user_history import UserHistory
from shared.enums import RiskCategory, SeverityColor, ConfidenceLevel
from config.constants import SEVERITY_THRESHOLDS, POLICY_MODE_MULTIPLIERS, CONFIDENCE_THRESHOLDS


def classify_risk(detected_elements: list[DetectedElement]) -> list[RiskCategory]:
    """
    Assign risk categories based on detected data types.
    Returns deduplicated list of categories found.
    """
    categories = set()
    for element in detected_elements:
        categories.add(element.category)
    return list(categories)


def calculate_risk_score(
    detected_categories: list[RiskCategory],
    data_volume: int,
    user_role: str,
    policy_mode: str,
    user_history: Optional[UserHistory] = None,
) -> float:
    """
    Produce a severity score (0-100) based on:
    - Risk categories detected
    - Volume of detected data
    - User's role and clearance
    - Policy mode multiplier
    - Historical behavior patterns
    """
    base_score = 0.0

    # Category weights
    category_weights = {
        RiskCategory.CREDENTIALS: 40,
        RiskCategory.REGULATED: 30,
        RiskCategory.FINANCIAL: 25,
        RiskCategory.PII: 20,
        RiskCategory.CUSTOMER_INFO: 20,
        RiskCategory.PROPRIETARY: 15,
        RiskCategory.INTERNAL_CODE_NAME: 15,
        RiskCategory.GENERAL: 5,
    }

    # Sum category weights
    for category in detected_categories:
        base_score += category_weights.get(category, 5)

    # Volume multiplier (more data = higher risk)
    volume_multiplier = min(1.0 + (data_volume * 0.1), 2.0)
    base_score *= volume_multiplier

    # Policy mode adjustment
    mode_multiplier = POLICY_MODE_MULTIPLIERS.get(policy_mode, 1.0)
    base_score /= mode_multiplier

    # Historical behavior adjustment
    if user_history and user_history.risk_trend == "WORSENING":
        base_score *= 1.2
    elif user_history and user_history.risk_trend == "IMPROVING":
        base_score *= 0.9

    # Clamp to 0-100
    return min(max(base_score, 0.0), 100.0)


def calculate_confidence(detected_elements: list[DetectedElement]) -> ConfidenceLevel:
    """
    Calculate overall detection confidence from individual element scores.
    """
    if not detected_elements:
        return ConfidenceLevel.LOW

    avg_confidence = sum(e.confidence for e in detected_elements) / len(detected_elements)

    if avg_confidence >= CONFIDENCE_THRESHOLDS["HIGH"]["min"]:
        return ConfidenceLevel.HIGH
    elif avg_confidence >= CONFIDENCE_THRESHOLDS["MEDIUM"]["min"]:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW


def map_risk_to_severity(risk_score: float, thresholds: PolicyThresholds) -> SeverityColor:
    """
    Translate risk score to Yellow, Orange, or Red severity color.
    """
    if risk_score >= thresholds.red_min:
        return SeverityColor.RED
    elif risk_score >= thresholds.orange_min:
        return SeverityColor.ORANGE
    else:
        return SeverityColor.YELLOW

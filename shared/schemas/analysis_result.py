"""
AnalysisResult — Developer 1 -> Developer 2 contract.

Contains all detected data types, risk score, severity color,
confidence score, recommended action, and rewrite if applicable.
"""

from typing import Optional
from pydantic import BaseModel
from shared.enums import RiskCategory, SeverityColor, ActionType, ConfidenceLevel, IntentType


class DetectedElement(BaseModel):
    """A single detected sensitive element within a prompt."""
    text: str
    category: RiskCategory
    start_index: int
    end_index: int
    confidence: float


class AnalysisResult(BaseModel):
    """Complete analysis output from the Gatekeeper (Developer 1)."""

    # Detected data
    detected_elements: list[DetectedElement] = []
    detected_categories: list[RiskCategory] = []
    intent: IntentType = IntentType.UNKNOWN

    # Risk assessment
    risk_score: float = 0.0
    severity_color: SeverityColor = SeverityColor.YELLOW
    confidence_level: ConfidenceLevel = ConfidenceLevel.LOW

    # Recommended action
    recommended_action: ActionType = ActionType.ALLOWED

    # Rewrite (if applicable)
    rewritten_prompt: Optional[str] = None
    rewrite_explanation: Optional[list[str]] = None

    # Metadata
    detectors_run: list[str] = []
    scan_duration_ms: float = 0.0

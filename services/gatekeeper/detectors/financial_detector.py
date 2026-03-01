"""
Financial Data Detector — Presidio plus custom rules.

Detects: revenue, pricing, margins, forecasts.
"""

from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory


# Financial keywords that indicate sensitive business data
FINANCIAL_KEYWORDS = [
    "revenue", "profit", "margin", "forecast", "budget",
    "earnings", "ebitda", "gross margin", "net income",
    "operating cost", "capex", "opex", "quarterly results",
    "pricing strategy", "cost structure", "market share",
    "year-over-year", "yoy", "guidance", "outlook",
]


def detect_financial_data(raw_prompt: str) -> list[DetectedElement]:
    """
    Detect financial figures and business-sensitive numeric data.

    Uses Presidio for number detection plus custom keyword matching
    for financial context terms like revenue, pricing, margins.
    """
    detected = []
    prompt_lower = raw_prompt.lower()

    # Check for financial keywords in context
    for keyword in FINANCIAL_KEYWORDS:
        start = 0
        while True:
            idx = prompt_lower.find(keyword, start)
            if idx == -1:
                break
            detected.append(
                DetectedElement(
                    text=raw_prompt[idx:idx + len(keyword)],
                    category=RiskCategory.FINANCIAL,
                    start_index=idx,
                    end_index=idx + len(keyword),
                    confidence=0.75,
                )
            )
            start = idx + 1

    # TODO: Combine with Presidio detection for financial figures
    # TODO: Cross-reference numeric data with financial context

    return detected

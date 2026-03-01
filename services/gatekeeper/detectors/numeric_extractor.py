"""
Numeric Data Extractor — identifies financial figures, account numbers, quantities.

Detects: dollar amounts, percentages, account numbers, logistics data.
"""

import re
from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory

# Patterns for numeric data
PATTERNS = {
    "dollar_amount": r"\$[\d,]+(?:\.\d{2})?",
    "percentage": r"\d+(?:\.\d+)?%",
    "account_number": r"\b\d{8,16}\b",
    "phone_number": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
}


def extract_numeric_data(raw_prompt: str) -> list[DetectedElement]:
    """
    Identify financial figures, account numbers, quantities, and logistics data.
    """
    detected = []

    for pattern_name, pattern in PATTERNS.items():
        matches = re.finditer(pattern, raw_prompt)
        for match in matches:
            category = RiskCategory.FINANCIAL if pattern_name in ("dollar_amount", "percentage") else RiskCategory.PII
            detected.append(
                DetectedElement(
                    text=match.group(),
                    category=category,
                    start_index=match.start(),
                    end_index=match.end(),
                    confidence=0.7,
                )
            )

    return detected

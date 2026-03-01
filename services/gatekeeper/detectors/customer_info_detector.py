"""
Customer Information Detector — customer names, accounts, purchase history.

Detects: customer names, account details, purchase history, contracts.
"""

from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory


# Keywords indicating customer-specific data
CUSTOMER_KEYWORDS = [
    "customer name", "client name", "account holder",
    "purchase order", "contract number", "agreement",
    "customer id", "client id", "buyer",
    "purchase history", "order history", "billing address",
    "shipping address", "delivery address",
]


def detect_customer_information(raw_prompt: str) -> list[DetectedElement]:
    """
    Detect customer names, account details, purchase history, and contract info.
    """
    detected = []
    prompt_lower = raw_prompt.lower()

    for keyword in CUSTOMER_KEYWORDS:
        start = 0
        while True:
            idx = prompt_lower.find(keyword, start)
            if idx == -1:
                break
            detected.append(
                DetectedElement(
                    text=raw_prompt[idx:idx + len(keyword)],
                    category=RiskCategory.CUSTOMER_INFO,
                    start_index=idx,
                    end_index=idx + len(keyword),
                    confidence=0.7,
                )
            )
            start = idx + 1

    # TODO: Use spaCy NER to detect customer names in context
    # TODO: Cross-reference with known customer name patterns

    return detected

"""
PII Detector — Microsoft Presidio integration.

Detects: names, SSNs, addresses, phone numbers, emails.
"""

from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory


def detect_pii(raw_prompt: str) -> list[DetectedElement]:
    """
    Use Microsoft Presidio to detect personally identifiable information.

    Detects:
    - Person names
    - Social Security Numbers
    - Physical addresses
    - Phone numbers
    - Email addresses
    """
    detected = []

    # TODO: Call integrations.presidio_client.analyze(raw_prompt)
    # TODO: Convert Presidio RecognizerResult objects to DetectedElement
    # TODO: Map Presidio entity types to RiskCategory.PII

    return detected

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

    try:
        from integrations.presidio_client import analyze_text
        results = analyze_text(raw_prompt)

        for result in results:
            detected.append(
                DetectedElement(
                    text=result["text"],
                    category=RiskCategory.PII,
                    start_index=result["start"],
                    end_index=result["end"],
                    confidence=result["score"],
                )
            )
    except Exception:
        # Fallback to basic regex if Presidio not available
        import re
        for match in re.finditer(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_prompt):
            detected.append(DetectedElement(
                text=match.group(), category=RiskCategory.PII,
                start_index=match.start(), end_index=match.end(), confidence=0.85,
            ))
        for match in re.finditer(r'\b\d{3}-\d{2}-\d{4}\b', raw_prompt):
            detected.append(DetectedElement(
                text=match.group(), category=RiskCategory.PII,
                start_index=match.start(), end_index=match.end(), confidence=0.95,
            ))
        for match in re.finditer(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', raw_prompt):
            detected.append(DetectedElement(
                text=match.group(), category=RiskCategory.PII,
                start_index=match.start(), end_index=match.end(), confidence=0.8,
            ))

    return detected

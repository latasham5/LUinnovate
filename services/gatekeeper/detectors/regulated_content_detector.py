"""
Regulated Content Detector — HIPAA, SOX, legal privilege detection.

Detects: health information, financial compliance data, legally privileged content.
"""

import re
from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory

# Keywords indicating regulated content
REGULATED_KEYWORDS = {
    "hipaa": [
        "patient", "diagnosis", "medical record", "health information",
        "treatment plan", "prescription", "hipaa", "phi",
        "protected health information", "medical history",
    ],
    "sox": [
        "sox compliance", "sarbanes-oxley", "internal controls",
        "financial statement", "audit finding", "material weakness",
        "disclosure", "10-k", "10-q", "sec filing",
    ],
    "legal_privilege": [
        "attorney-client", "legal privilege", "privileged communication",
        "legal counsel", "litigation", "settlement",
        "confidential legal", "work product",
    ],
}


def detect_regulated_content(raw_prompt: str) -> list[DetectedElement]:
    """
    Detect content subject to HIPAA, SOX, or legal privilege protections.
    """
    detected = []
    prompt_lower = raw_prompt.lower()

    for regulation_type, keywords in REGULATED_KEYWORDS.items():
        for keyword in keywords:
            idx = prompt_lower.find(keyword)
            if idx != -1:
                detected.append(
                    DetectedElement(
                        text=raw_prompt[idx:idx + len(keyword)],
                        category=RiskCategory.REGULATED,
                        start_index=idx,
                        end_index=idx + len(keyword),
                        confidence=0.8,
                    )
                )

    return detected

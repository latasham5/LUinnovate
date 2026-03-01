"""
Internal Code Name Detector — project names, initiative titles, unreleased products.

Detects: internal project names, initiative titles, unreleased product names.
"""

import json
import os
from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory

# Path to the code name patterns file
PATTERNS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "patterns", "code_name_patterns.json")


def _load_code_names() -> list[str]:
    """Load internal code names from the patterns file."""
    try:
        with open(PATTERNS_FILE, "r") as f:
            data = json.load(f)
            return data.get("code_names", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def detect_internal_code_names(raw_prompt: str) -> list[DetectedElement]:
    """
    Detect project names, initiative titles, and unreleased product references.

    Matches against a configurable list of known internal code names.
    """
    detected = []
    code_names = _load_code_names()
    prompt_lower = raw_prompt.lower()

    for code_name in code_names:
        idx = prompt_lower.find(code_name.lower())
        if idx != -1:
            detected.append(
                DetectedElement(
                    text=raw_prompt[idx:idx + len(code_name)],
                    category=RiskCategory.INTERNAL_CODE_NAME,
                    start_index=idx,
                    end_index=idx + len(code_name),
                    confidence=0.9,
                )
            )

    return detected

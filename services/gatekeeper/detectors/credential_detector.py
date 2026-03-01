"""
Credential Detector — regex patterns for secrets.

Detects: passwords, API keys, tokens, internal URLs.
"""

import re
from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory

# Regex patterns for credential detection
CREDENTIAL_PATTERNS = {
    "api_key": r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
    "bearer_token": r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}",
    "password": r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?(\S{6,})['\"]?",
    "secret_key": r"(?i)(secret[_-]?key|client[_-]?secret)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?",
    "aws_key": r"(?i)AKIA[0-9A-Z]{16}",
    "private_key": r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
    "internal_url": r"https?://(?:internal|intranet|corp|private)[.\-][a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:/\S*)?",
    "connection_string": r"(?i)(mongodb|postgresql|mysql|redis|amqp)://\S+",
    "jwt_token": r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
}


def detect_credentials(raw_prompt: str) -> list[DetectedElement]:
    """
    Scan for passwords, API keys, tokens, and internal URLs using regex patterns.
    Credentials are always HIGH severity — blocked regardless of deployment mode.
    """
    detected = []

    for pattern_name, pattern in CREDENTIAL_PATTERNS.items():
        matches = re.finditer(pattern, raw_prompt)
        for match in matches:
            detected.append(
                DetectedElement(
                    text=match.group(),
                    category=RiskCategory.CREDENTIALS,
                    start_index=match.start(),
                    end_index=match.end(),
                    confidence=0.95,  # High confidence for regex matches
                )
            )

    return detected

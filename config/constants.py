"""
Application-wide constants and configuration values.
"""

# Risk score thresholds for severity mapping
SEVERITY_THRESHOLDS = {
    "YELLOW": {"min": 1, "max": 39},   # Low risk — log only, weekly digest
    "ORANGE": {"min": 40, "max": 69},  # Medium risk — real-time manager notification
    "RED": {"min": 70, "max": 100},    # High risk — immediate manager + cybersecurity
}

# Policy mode risk threshold multipliers
POLICY_MODE_MULTIPLIERS = {
    "STRICT": 0.7,    # Lower thresholds = more sensitive
    "BALANCED": 1.0,   # Default thresholds
    "FAST": 1.3,       # Higher thresholds = less sensitive
}

# Confidence score thresholds
CONFIDENCE_THRESHOLDS = {
    "LOW": {"min": 0.0, "max": 0.39},
    "MEDIUM": {"min": 0.4, "max": 0.69},
    "HIGH": {"min": 0.7, "max": 1.0},
}

# Default micro-training trigger (flags before training is assigned)
DEFAULT_FLAG_THRESHOLD = 5

# Session timeout in minutes
SESSION_TIMEOUT_MINUTES = 30

# Data retention period in days
DEFAULT_RETENTION_DAYS = 365

# Hugging Face model identifiers
HF_INTENT_MODEL = "facebook/bart-large-mnli"
HF_RISKY_INTENT_MODEL = "unitary/toxic-bert"

# spaCy model
SPACY_MODEL = "en_core_web_sm"

"""
Shared enumerations used across all three developer domains.
"""

from enum import Enum


class RiskCategory(str, Enum):
    """Risk categories for detected sensitive data."""
    FINANCIAL = "FINANCIAL"
    CREDENTIALS = "CREDENTIALS"
    PII = "PII"
    CUSTOMER_INFO = "CUSTOMER_INFO"
    PROPRIETARY = "PROPRIETARY"
    INTERNAL_CODE_NAME = "INTERNAL_CODE_NAME"
    REGULATED = "REGULATED"
    GENERAL = "GENERAL"


class SeverityColor(str, Enum):
    """Severity levels mapped to colors."""
    YELLOW = "YELLOW"   # Low — log only, weekly digest
    ORANGE = "ORANGE"   # Medium — real-time manager notification
    RED = "RED"         # High — immediate manager + cybersecurity alert


class ActionType(str, Enum):
    """Actions that can be taken on a prompt."""
    ALLOWED = "ALLOWED"
    ALLOWED_WITH_WARNING = "ALLOWED_WITH_WARNING"
    REWRITTEN = "REWRITTEN"
    BLOCKED = "BLOCKED"
    SHADOW_LOGGED = "SHADOW_LOGGED"


class PolicyMode(str, Enum):
    """Policy enforcement sensitivity modes."""
    STRICT = "STRICT"
    BALANCED = "BALANCED"
    FAST = "FAST"


class DeploymentMode(str, Enum):
    """System deployment modes."""
    SHADOW = "SHADOW"
    FULL_ENFORCEMENT = "FULL_ENFORCEMENT"


class ConfidenceLevel(str, Enum):
    """Detection confidence levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class IntentType(str, Enum):
    """Classified user intent types."""
    QUESTION = "QUESTION"
    DATA_PASTE = "DATA_PASTE"
    CONTENT_GENERATION = "CONTENT_GENERATION"
    DATA_EXTRACTION = "DATA_EXTRACTION"
    SUMMARIZATION = "SUMMARIZATION"
    UNKNOWN = "UNKNOWN"


class UserRole(str, Enum):
    """User role types."""
    EMPLOYEE = "EMPLOYEE"
    SUPERVISOR = "SUPERVISOR"
    DEPARTMENT_ADMIN = "DEPARTMENT_ADMIN"
    CYBERSECURITY = "CYBERSECURITY"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

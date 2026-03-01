"""
Custom exceptions for the Phantom App.
"""


class PhantomBaseException(Exception):
    """Base exception for all Phantom App errors."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


# === Gatekeeper Exceptions (Developer 1) ===

class DetectionError(PhantomBaseException):
    """Raised when a detection function fails."""

    def __init__(self, detector_name: str, detail: str):
        super().__init__(
            message=f"Detection failed in {detector_name}: {detail}",
            code="DETECTION_ERROR",
        )


class RewriteError(PhantomBaseException):
    """Raised when the rewrite engine fails to produce a safe prompt."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Rewrite engine failure: {detail}",
            code="REWRITE_ERROR",
        )


class RiskClassificationError(PhantomBaseException):
    """Raised when risk classification fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Risk classification error: {detail}",
            code="RISK_CLASSIFICATION_ERROR",
        )


# === Enforcer Exceptions (Developer 2) ===

class AuthenticationError(PhantomBaseException):
    """Raised when SSO token validation fails."""

    def __init__(self, detail: str = "Invalid or expired SSO token"):
        super().__init__(message=detail, code="AUTH_ERROR")


class AuthorizationError(PhantomBaseException):
    """Raised when user lacks required permissions."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(message=detail, code="AUTHORIZATION_ERROR")


class PolicyError(PhantomBaseException):
    """Raised when policy lookup or evaluation fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Policy error: {detail}",
            code="POLICY_ERROR",
        )


class CokeGPTError(PhantomBaseException):
    """Raised when CokeGPT communication fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"CokeGPT error: {detail}",
            code="COKEGPT_ERROR",
        )


class PromptBlockedError(PhantomBaseException):
    """Raised when a prompt is blocked by policy."""

    def __init__(self, reason: str, risk_category: str):
        super().__init__(
            message=f"Prompt blocked: {reason}",
            code="PROMPT_BLOCKED",
        )
        self.risk_category = risk_category


# === Watchtower Exceptions (Developer 3) ===

class LoggingError(PhantomBaseException):
    """Raised when logging to Supabase fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Logging error: {detail}",
            code="LOGGING_ERROR",
        )


class AlertingError(PhantomBaseException):
    """Raised when alert dispatch fails."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Alerting error: {detail}",
            code="ALERTING_ERROR",
        )


class TrainingError(PhantomBaseException):
    """Raised when micro-training operations fail."""

    def __init__(self, detail: str):
        super().__init__(
            message=f"Training error: {detail}",
            code="TRAINING_ERROR",
        )

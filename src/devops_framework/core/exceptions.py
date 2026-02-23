"""Custom exception hierarchy for the DevOps Framework."""


class DevOpsFrameworkError(Exception):
    """Base exception for all DevOps Framework errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | details={self.details}"
        return self.message


# ── Authentication ────────────────────────────────────────────────────────────

class AuthenticationError(DevOpsFrameworkError):
    """Raised when authentication with an integration fails."""


class AWSAuthError(AuthenticationError):
    """Raised when AWS authentication fails."""


class DatadogAuthError(AuthenticationError):
    """Raised when Datadog authentication fails."""


class EKSAuthError(AuthenticationError):
    """Raised when EKS/Kubernetes authentication fails."""


# ── Resource ──────────────────────────────────────────────────────────────────

class ResourceNotFoundError(DevOpsFrameworkError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource_type: str, identifier: str) -> None:
        super().__init__(
            f"{resource_type} '{identifier}' not found",
            details={"resource_type": resource_type, "identifier": identifier},
        )
        self.resource_type = resource_type
        self.identifier = identifier


# ── API Errors ────────────────────────────────────────────────────────────────

class IntegrationAPIError(DevOpsFrameworkError):
    """Raised when an integration API call fails."""

    def __init__(self, message: str, status_code: int | None = None, details: dict | None = None) -> None:
        super().__init__(message, details)
        self.status_code = status_code


class AWSAPIError(IntegrationAPIError):
    """Raised when an AWS API call fails."""


class DatadogAPIError(IntegrationAPIError):
    """Raised when a Datadog API call fails."""


class KubernetesAPIError(IntegrationAPIError):
    """Raised when a Kubernetes API call fails."""


# ── Configuration ─────────────────────────────────────────────────────────────

class ConfigurationError(DevOpsFrameworkError):
    """Raised when configuration is missing or invalid."""

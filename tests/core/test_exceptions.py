"""Tests for core/exceptions.py."""

from __future__ import annotations

import pytest

from devops_framework.core.exceptions import (
    AWSAPIError,
    AWSAuthError,
    AuthenticationError,
    ConfigurationError,
    DatadogAPIError,
    DatadogAuthError,
    DevOpsFrameworkError,
    EKSAuthError,
    IntegrationAPIError,
    KubernetesAPIError,
    ResourceNotFoundError,
)


def test_base_exception_message() -> None:
    exc = DevOpsFrameworkError("Something went wrong")
    assert str(exc) == "Something went wrong"
    assert exc.message == "Something went wrong"
    assert exc.details == {}


def test_base_exception_with_details() -> None:
    exc = DevOpsFrameworkError("Error", details={"key": "value"})
    assert "key" in str(exc)
    assert "value" in str(exc)


def test_resource_not_found_error() -> None:
    exc = ResourceNotFoundError("EC2 Instance", "i-12345")
    assert "EC2 Instance" in str(exc)
    assert "i-12345" in str(exc)
    assert exc.resource_type == "EC2 Instance"
    assert exc.identifier == "i-12345"


def test_integration_api_error_status_code() -> None:
    exc = AWSAPIError("API failed", status_code=500)
    assert exc.status_code == 500


def test_exception_hierarchy() -> None:
    assert issubclass(AWSAuthError, AuthenticationError)
    assert issubclass(DatadogAuthError, AuthenticationError)
    assert issubclass(EKSAuthError, AuthenticationError)
    assert issubclass(AuthenticationError, DevOpsFrameworkError)

    assert issubclass(AWSAPIError, IntegrationAPIError)
    assert issubclass(DatadogAPIError, IntegrationAPIError)
    assert issubclass(KubernetesAPIError, IntegrationAPIError)
    assert issubclass(IntegrationAPIError, DevOpsFrameworkError)

    assert issubclass(ResourceNotFoundError, DevOpsFrameworkError)
    assert issubclass(ConfigurationError, DevOpsFrameworkError)


def test_all_exceptions_are_catchable_as_base() -> None:
    exceptions = [
        AWSAuthError("aws auth"),
        DatadogAuthError("dd auth"),
        EKSAuthError("eks auth"),
        ResourceNotFoundError("Pod", "my-pod"),
        AWSAPIError("aws api"),
        DatadogAPIError("dd api"),
        KubernetesAPIError("k8s api"),
        ConfigurationError("config"),
    ]
    for exc in exceptions:
        assert isinstance(exc, DevOpsFrameworkError)

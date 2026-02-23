"""Shared test fixtures: moto for AWS, mocks for EKS and Datadog."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

from devops_framework.core.config import Config


# ── Helpers ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_aws_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure AWS env vars don't bleed from real credentials during tests."""
    for var in ("AWS_PROFILE", "AWS_DEFAULT_REGION", "AWS_REGION"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")


@pytest.fixture()
def aws_config() -> Config:
    return Config()


# ── moto AWS mock ─────────────────────────────────────────────────────────────

@pytest.fixture()
def moto_aws():
    """Start moto mock_aws context for all AWS services."""
    with mock_aws():
        yield


@pytest.fixture()
def ec2_resource(moto_aws: None):
    """Provide a boto3 EC2 resource inside moto context."""
    return boto3.resource("ec2", region_name="us-east-1")


@pytest.fixture()
def ec2_client_boto(moto_aws: None):
    """Provide a raw boto3 EC2 client inside moto context."""
    return boto3.client("ec2", region_name="us-east-1")


@pytest.fixture()
def sample_instance(ec2_resource):
    """Create a single EC2 instance and return its boto3 Instance object."""
    [instance] = ec2_resource.create_instances(
        ImageId="ami-00000000",
        MinCount=1,
        MaxCount=1,
        InstanceType="t3.micro",
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Name", "Value": "test-instance"}],
            }
        ],
    )
    return instance


# ── Kubernetes mock ───────────────────────────────────────────────────────────

@pytest.fixture()
def mock_kube_config():
    """Patch kubernetes config loaders so no real kubeconfig is needed."""
    with patch("kubernetes.config.load_kube_config") as mock_load:
        yield mock_load


@pytest.fixture()
def mock_core_v1():
    """Return a MagicMock for kubernetes.client.CoreV1Api."""
    with patch("kubernetes.client.CoreV1Api") as MockApi:
        yield MockApi.return_value


@pytest.fixture()
def mock_apps_v1():
    """Return a MagicMock for kubernetes.client.AppsV1Api."""
    with patch("kubernetes.client.AppsV1Api") as MockApi:
        yield MockApi.return_value


# ── Datadog mock ──────────────────────────────────────────────────────────────

@pytest.fixture()
def dd_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set fake Datadog credentials via env vars."""
    monkeypatch.setenv("DD_API_KEY", "fake-api-key")
    monkeypatch.setenv("DD_APP_KEY", "fake-app-key")


@pytest.fixture()
def mock_dd_api_client():
    """Patch datadog_api_client.ApiClient context manager."""
    with patch("datadog_api_client.ApiClient") as MockClient:
        instance = MagicMock()
        MockClient.return_value.__enter__ = MagicMock(return_value=instance)
        MockClient.return_value.__exit__ = MagicMock(return_value=False)
        yield MockClient, instance

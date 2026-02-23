"""Tests for eks/deployments.py using kubernetes mocks."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from devops_framework.core.exceptions import ResourceNotFoundError
from devops_framework.eks.deployments import DeploymentClient


@pytest.fixture()
def deployment_client(mock_kube_config: MagicMock) -> DeploymentClient:
    client = DeploymentClient(namespace="default")
    client._k8s_config_loaded = True
    return client


def _make_deployment(name: str, desired: int = 3, ready: int = 3) -> MagicMock:
    dep = MagicMock()
    dep.metadata.name = name
    dep.spec.replicas = desired
    dep.status.ready_replicas = ready
    dep.status.updated_replicas = desired
    dep.status.available_replicas = ready
    return dep


def test_list_deployments_empty(deployment_client: DeploymentClient) -> None:
    with patch.object(deployment_client, "apps_v1") as mock_apps:
        mock_apps.list_namespaced_deployment.return_value.items = []
        deployments = deployment_client.list_deployments()
        assert deployments == []


def test_list_deployments_returns_items(deployment_client: DeploymentClient) -> None:
    fake_deps = [_make_deployment("dep-1"), _make_deployment("dep-2")]
    with patch.object(deployment_client, "apps_v1") as mock_apps:
        mock_apps.list_namespaced_deployment.return_value.items = fake_deps
        deployments = deployment_client.list_deployments()
        assert len(deployments) == 2


def test_get_deployment_success(deployment_client: DeploymentClient) -> None:
    fake_dep = _make_deployment("dep-1")
    with patch.object(deployment_client, "apps_v1") as mock_apps:
        mock_apps.read_namespaced_deployment.return_value = fake_dep
        dep = deployment_client.get_deployment("dep-1")
        assert dep.metadata.name == "dep-1"


def test_get_deployment_not_found(deployment_client: DeploymentClient) -> None:
    from kubernetes.client.exceptions import ApiException

    with patch.object(deployment_client, "apps_v1") as mock_apps:
        mock_apps.read_namespaced_deployment.side_effect = ApiException(status=404, reason="Not Found")
        with pytest.raises(ResourceNotFoundError):
            deployment_client.get_deployment("nonexistent")


def test_scale_deployment(deployment_client: DeploymentClient) -> None:
    fake_dep = _make_deployment("dep-1", desired=5, ready=5)
    with patch.object(deployment_client, "apps_v1") as mock_apps:
        mock_apps.patch_namespaced_deployment_scale.return_value = fake_dep
        result = deployment_client.scale_deployment("dep-1", replicas=5)
        mock_apps.patch_namespaced_deployment_scale.assert_called_once()
        assert result.spec.replicas == 5

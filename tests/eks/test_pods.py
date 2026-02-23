"""Tests for eks/pods.py using kubernetes mocks."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from devops_framework.core.exceptions import ResourceNotFoundError
from devops_framework.eks.pods import PodClient


@pytest.fixture()
def pod_client(mock_kube_config: MagicMock) -> PodClient:
    client = PodClient(namespace="default")
    client._k8s_config_loaded = True  # skip config load in tests
    return client


def _make_pod(name: str, phase: str = "Running") -> MagicMock:
    pod = MagicMock()
    pod.metadata.name = name
    pod.status.phase = phase
    pod.status.container_statuses = []
    pod.spec.node_name = "node-1"
    return pod


def test_list_pods_empty(pod_client: PodClient) -> None:
    with patch.object(pod_client, "core_v1") as mock_core:
        mock_core.list_namespaced_pod.return_value.items = []
        pods = pod_client.list_pods()
        assert pods == []


def test_list_pods_returns_items(pod_client: PodClient) -> None:
    fake_pods = [_make_pod("pod-1"), _make_pod("pod-2")]
    with patch.object(pod_client, "core_v1") as mock_core:
        mock_core.list_namespaced_pod.return_value.items = fake_pods
        pods = pod_client.list_pods()
        assert len(pods) == 2


def test_get_pod_success(pod_client: PodClient) -> None:
    fake_pod = _make_pod("pod-1")
    with patch.object(pod_client, "core_v1") as mock_core:
        mock_core.read_namespaced_pod.return_value = fake_pod
        pod = pod_client.get_pod("pod-1")
        assert pod.metadata.name == "pod-1"


def test_get_pod_not_found(pod_client: PodClient) -> None:
    from kubernetes.client.exceptions import ApiException

    with patch.object(pod_client, "core_v1") as mock_core:
        exc = ApiException(status=404, reason="Not Found")
        mock_core.read_namespaced_pod.side_effect = exc
        with pytest.raises(ResourceNotFoundError):
            pod_client.get_pod("nonexistent")


def test_get_pod_logs(pod_client: PodClient) -> None:
    with patch.object(pod_client, "core_v1") as mock_core:
        mock_core.read_namespaced_pod_log.return_value = "log line 1\nlog line 2"
        logs = pod_client.get_pod_logs("pod-1")
        assert "log line 1" in logs


def test_delete_pod(pod_client: PodClient) -> None:
    with patch.object(pod_client, "core_v1") as mock_core:
        pod_client.delete_pod("pod-1")
        mock_core.delete_namespaced_pod.assert_called_once_with(name="pod-1", namespace="default")

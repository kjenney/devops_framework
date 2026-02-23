"""Tests for eks/services.py using kubernetes mocks."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from devops_framework.core.exceptions import ResourceNotFoundError
from devops_framework.eks.services import ServiceClient


@pytest.fixture()
def service_client(mock_kube_config: MagicMock) -> ServiceClient:
    client = ServiceClient(namespace="default")
    client._k8s_config_loaded = True
    return client


def _make_service(name: str, svc_type: str = "ClusterIP") -> MagicMock:
    svc = MagicMock()
    svc.metadata.name = name
    svc.spec.type = svc_type
    svc.spec.cluster_ip = "10.0.0.1"
    svc.spec.external_i_ps = []
    svc.spec.ports = []
    return svc


def test_list_services_empty(service_client: ServiceClient) -> None:
    with patch.object(service_client, "core_v1") as mock_core:
        mock_core.list_namespaced_service.return_value.items = []
        services = service_client.list_services()
        assert services == []


def test_list_services_returns_items(service_client: ServiceClient) -> None:
    fake_services = [_make_service("svc-1"), _make_service("svc-2")]
    with patch.object(service_client, "core_v1") as mock_core:
        mock_core.list_namespaced_service.return_value.items = fake_services
        services = service_client.list_services()
        assert len(services) == 2


def test_get_service_success(service_client: ServiceClient) -> None:
    fake_svc = _make_service("svc-1")
    with patch.object(service_client, "core_v1") as mock_core:
        mock_core.read_namespaced_service.return_value = fake_svc
        svc = service_client.get_service("svc-1")
        assert svc.metadata.name == "svc-1"


def test_get_service_not_found(service_client: ServiceClient) -> None:
    from kubernetes.client.exceptions import ApiException

    with patch.object(service_client, "core_v1") as mock_core:
        mock_core.read_namespaced_service.side_effect = ApiException(status=404, reason="Not Found")
        with pytest.raises(ResourceNotFoundError):
            service_client.get_service("nonexistent")


def test_get_endpoints(service_client: ServiceClient) -> None:
    fake_ep = MagicMock()
    with patch.object(service_client, "core_v1") as mock_core:
        mock_core.read_namespaced_endpoints.return_value = fake_ep
        ep = service_client.get_endpoints("svc-1")
        assert ep is fake_ep

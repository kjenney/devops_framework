"""Tests for cli/eks.py using Typer's CliRunner and mocked clients."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from devops_framework.cli.main import app

runner = CliRunner()


def _make_pod(name: str) -> MagicMock:
    pod = MagicMock()
    pod.metadata.name = name
    pod.status.phase = "Running"
    pod.status.container_statuses = []
    pod.spec.node_name = "node-1"
    return pod


def _make_deployment(name: str) -> MagicMock:
    dep = MagicMock()
    dep.metadata.name = name
    dep.spec.replicas = 3
    dep.status.ready_replicas = 3
    dep.status.updated_replicas = 3
    dep.status.available_replicas = 3
    return dep


def _make_service(name: str) -> MagicMock:
    svc = MagicMock()
    svc.metadata.name = name
    svc.spec.type = "ClusterIP"
    svc.spec.cluster_ip = "10.0.0.1"
    svc.spec.external_i_ps = []
    svc.spec.ports = []
    return svc


def test_eks_help() -> None:
    result = runner.invoke(app, ["eks", "--help"])
    assert result.exit_code == 0


def test_list_pods_empty() -> None:
    with patch("devops_framework.cli.eks.PodClient") as MockPod:
        MockPod.return_value.list_pods.return_value = []
        result = runner.invoke(app, ["eks", "list-pods"])
    assert result.exit_code == 0


def test_list_pods_with_data() -> None:
    with patch("devops_framework.cli.eks.PodClient") as MockPod:
        MockPod.return_value.list_pods.return_value = [_make_pod("test-pod")]
        result = runner.invoke(app, ["eks", "list-pods"])
    assert result.exit_code == 0
    assert "test-pod" in result.output


def test_list_deployments_empty() -> None:
    with patch("devops_framework.cli.eks.DeploymentClient") as MockDep:
        MockDep.return_value.list_deployments.return_value = []
        result = runner.invoke(app, ["eks", "list-deployments"])
    assert result.exit_code == 0


def test_list_services_empty() -> None:
    with patch("devops_framework.cli.eks.ServiceClient") as MockSvc:
        MockSvc.return_value.list_services.return_value = []
        result = runner.invoke(app, ["eks", "list-services"])
    assert result.exit_code == 0


def test_get_pod_logs() -> None:
    with patch("devops_framework.cli.eks.PodClient") as MockPod:
        MockPod.return_value.get_pod_logs.return_value = "line1\nline2"
        result = runner.invoke(app, ["eks", "get-pod-logs", "my-pod"])
    assert result.exit_code == 0
    assert "line1" in result.output

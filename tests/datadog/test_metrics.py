"""Tests for datadog/metrics.py using mocks."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from devops_framework.core.exceptions import DatadogAPIError
from devops_framework.datadog.metrics import MetricsClient


@pytest.fixture()
def metrics_client(dd_env: None) -> MetricsClient:
    return MetricsClient()


def test_query_metrics_returns_dict(metrics_client: MetricsClient) -> None:
    fake_resp = MagicMock()
    fake_resp.to_dict.return_value = {"series": [{"metric": "system.cpu.user", "pointlist": [[1, 2.5]]}]}

    with patch("devops_framework.datadog.metrics.ApiClient"), \
         patch("devops_framework.datadog.metrics.MetricsApi") as MockApi:
        MockApi.return_value.query_metrics.return_value = fake_resp
        result = metrics_client.query_metrics("avg:system.cpu.user{*}")
        assert "series" in result


def test_query_metrics_api_error(metrics_client: MetricsClient) -> None:
    with patch("devops_framework.datadog.metrics.ApiClient"), \
         patch("devops_framework.datadog.metrics.MetricsApi") as MockApi:
        MockApi.return_value.query_metrics.side_effect = Exception("API failure")
        with pytest.raises(DatadogAPIError, match="metrics query failed"):
            metrics_client.query_metrics("avg:system.cpu.user{*}")


def test_list_active_metrics(metrics_client: MetricsClient) -> None:
    fake_resp = MagicMock()
    fake_resp.metrics = ["system.cpu.user", "system.mem.used"]

    with patch("devops_framework.datadog.metrics.ApiClient"), \
         patch("devops_framework.datadog.metrics.MetricsApi") as MockApi:
        MockApi.return_value.list_active_metrics.return_value = fake_resp
        metrics = metrics_client.list_active_metrics()
        assert "system.cpu.user" in metrics


def test_get_metric_metadata(metrics_client: MetricsClient) -> None:
    fake_resp = MagicMock()
    fake_resp.to_dict.return_value = {"type": "gauge", "unit": "percent"}

    with patch("devops_framework.datadog.metrics.ApiClient"), \
         patch("devops_framework.datadog.metrics.MetricsApi") as MockApi:
        MockApi.return_value.get_metric_metadata.return_value = fake_resp
        metadata = metrics_client.get_metric_metadata("system.cpu.user")
        assert metadata["type"] == "gauge"

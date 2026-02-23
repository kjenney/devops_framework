"""Tests for cli/datadog.py using Typer's CliRunner and mocked clients."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from devops_framework.cli.main import app

runner = CliRunner()


def test_datadog_help() -> None:
    result = runner.invoke(app, ["datadog", "--help"])
    assert result.exit_code == 0


def test_query_metrics_empty(dd_env: None) -> None:
    with patch("devops_framework.cli.datadog.MetricsClient") as MockMetrics:
        MockMetrics.return_value.query_metrics.return_value = {"series": []}
        result = runner.invoke(app, ["datadog", "query-metrics", "--query", "avg:system.cpu.user{*}"])
    assert result.exit_code == 0
    assert "No data" in result.output


def test_query_metrics_with_data(dd_env: None) -> None:
    with patch("devops_framework.cli.datadog.MetricsClient") as MockMetrics:
        MockMetrics.return_value.query_metrics.return_value = {
            "series": [
                {"metric": "system.cpu.user", "scope": "*", "pointlist": [[1, 2.5]]}
            ]
        }
        result = runner.invoke(app, ["datadog", "query-metrics", "--query", "avg:system.cpu.user{*}"])
    assert result.exit_code == 0
    assert "system.cpu.user" in result.output


def test_search_logs_empty(dd_env: None) -> None:
    with patch("devops_framework.cli.datadog.LogsClient") as MockLogs:
        MockLogs.return_value.search_logs.return_value = []
        result = runner.invoke(app, ["datadog", "search-logs"])
    assert result.exit_code == 0
    assert "No logs" in result.output


def test_list_metrics_with_data(dd_env: None) -> None:
    with patch("devops_framework.cli.datadog.MetricsClient") as MockMetrics:
        MockMetrics.return_value.list_active_metrics.return_value = ["system.cpu.user", "system.mem.used"]
        result = runner.invoke(app, ["datadog", "list-metrics"])
    assert result.exit_code == 0
    assert "system.cpu.user" in result.output

"""Tests for datadog/logs.py using mocks."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from devops_framework.core.exceptions import DatadogAuthError, DatadogAPIError
from devops_framework.datadog.logs import LogsClient


@pytest.fixture()
def logs_client(dd_env: None) -> LogsClient:
    return LogsClient()


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DD_API_KEY", raising=False)
    monkeypatch.delenv("DD_APP_KEY", raising=False)
    with pytest.raises(DatadogAuthError, match="API key"):
        LogsClient()


def test_missing_app_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DD_API_KEY", "key")
    monkeypatch.delenv("DD_APP_KEY", raising=False)
    with pytest.raises(DatadogAuthError, match="Application key"):
        LogsClient()


def test_search_logs_returns_list(logs_client: LogsClient) -> None:
    fake_log = MagicMock()
    fake_log.to_dict.return_value = {"id": "abc", "attributes": {"message": "hello"}}

    mock_resp = MagicMock()
    mock_resp.data = [fake_log]

    with patch("devops_framework.datadog.logs.ApiClient"), \
         patch("devops_framework.datadog.logs.LogsApi") as MockApi:
        MockApi.return_value.list_logs.return_value = mock_resp
        logs = logs_client.search_logs(query="*")
        assert len(logs) == 1
        assert logs[0]["id"] == "abc"


def test_search_logs_api_error(logs_client: LogsClient) -> None:
    with patch("devops_framework.datadog.logs.ApiClient"), \
         patch("devops_framework.datadog.logs.LogsApi") as MockApi:
        MockApi.return_value.list_logs.side_effect = Exception("API failure")
        with pytest.raises(DatadogAPIError, match="logs search failed"):
            logs_client.search_logs()

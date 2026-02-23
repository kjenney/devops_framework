"""Datadog Metrics client."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from datadog_api_client import ApiClient
from datadog_api_client.v1.api.metrics_api import MetricsApi

from devops_framework.core.exceptions import DatadogAPIError
from devops_framework.datadog.base import DatadogBaseClient


class MetricsClient(DatadogBaseClient):
    """Client for Datadog Metrics API (v1)."""

    def query_metrics(
        self,
        query: str,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Query a Datadog metrics expression.

        ``from_time`` and ``to_time`` default to last 1 hour if not provided.
        Returns the raw API response dict.
        """
        now = int(datetime.now().timestamp())
        _from = int(from_time.timestamp()) if from_time else now - 3600
        _to = int(to_time.timestamp()) if to_time else now

        try:
            with ApiClient(self._dd_configuration) as client:
                api = MetricsApi(client)
                resp = api.query_metrics(start=_from, end=_to, query=query)
        except Exception as exc:
            raise DatadogAPIError(f"Datadog metrics query failed: {exc}") from exc

        return resp.to_dict()

    def list_active_metrics(self, from_time: datetime | None = None, host: str | None = None) -> list[str]:
        """
        Return a list of actively reporting metric names.

        ``from_time`` defaults to 24 hours ago.
        """
        now = int(datetime.now().timestamp())
        _from = int(from_time.timestamp()) if from_time else now - 86400

        kwargs: dict[str, Any] = {"_from": _from}
        if host:
            kwargs["host"] = host

        try:
            with ApiClient(self._dd_configuration) as client:
                api = MetricsApi(client)
                resp = api.list_active_metrics(**kwargs)
        except Exception as exc:
            raise DatadogAPIError(f"Datadog list_active_metrics failed: {exc}") from exc

        return list(resp.metrics or [])

    def get_metric_metadata(self, metric_name: str) -> dict[str, Any]:
        """Return metadata for a specific metric."""
        try:
            with ApiClient(self._dd_configuration) as client:
                api = MetricsApi(client)
                resp = api.get_metric_metadata(metric_name=metric_name)
        except Exception as exc:
            raise DatadogAPIError(f"Datadog get_metric_metadata({metric_name}) failed: {exc}") from exc

        return resp.to_dict()

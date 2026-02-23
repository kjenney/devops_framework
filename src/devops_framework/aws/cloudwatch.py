"""CloudWatch client for metrics and log groups."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import cached_property
from typing import Any

from botocore.exceptions import ClientError

from devops_framework.aws.base import AWSBaseClient
from devops_framework.core.exceptions import ResourceNotFoundError


class CloudWatchClient(AWSBaseClient):
    """Client for CloudWatch metrics and CloudWatch Logs."""

    @cached_property
    def _cw(self) -> Any:
        return self._boto_client("cloudwatch")

    @cached_property
    def _logs(self) -> Any:
        return self._boto_client("logs")

    # ── Metrics ───────────────────────────────────────────────────────────────

    def get_metric_statistics(
        self,
        namespace: str,
        metric_name: str,
        dimensions: list[dict[str, str]],
        start_time: datetime,
        end_time: datetime,
        period: int = 300,
        statistics: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Return datapoints for a CloudWatch metric.

        ``period`` is in seconds (default 5 min). ``statistics`` defaults to ["Average"].
        """
        if statistics is None:
            statistics = ["Average"]
        try:
            resp = self._cw.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=statistics,
            )
        except ClientError as exc:
            raise self._wrap_client_error(exc, "CloudWatch get_metric_statistics failed") from exc
        return sorted(resp.get("Datapoints", []), key=lambda d: d["Timestamp"])

    def list_metrics(
        self,
        namespace: str | None = None,
        metric_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """List CloudWatch metrics, optionally filtered by namespace and/or name."""
        kwargs: dict[str, Any] = {}
        if namespace:
            kwargs["Namespace"] = namespace
        if metric_name:
            kwargs["MetricName"] = metric_name
        metrics: list[dict[str, Any]] = []
        try:
            paginator = self._cw.get_paginator("list_metrics")
            for page in paginator.paginate(**kwargs):
                metrics.extend(page.get("Metrics", []))
        except ClientError as exc:
            raise self._wrap_client_error(exc, "CloudWatch list_metrics failed") from exc
        return metrics

    # ── Logs ──────────────────────────────────────────────────────────────────

    def list_log_groups(self, prefix: str | None = None) -> list[dict[str, Any]]:
        """List CloudWatch Log groups, optionally filtered by name prefix."""
        kwargs: dict[str, Any] = {}
        if prefix:
            kwargs["logGroupNamePrefix"] = prefix
        groups: list[dict[str, Any]] = []
        try:
            paginator = self._logs.get_paginator("describe_log_groups")
            for page in paginator.paginate(**kwargs):
                groups.extend(page.get("logGroups", []))
        except ClientError as exc:
            raise self._wrap_client_error(exc, "CloudWatch Logs describe_log_groups failed") from exc
        return groups

    def get_log_events(
        self,
        log_group_name: str,
        log_stream_name: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return events from a specific log stream."""
        kwargs: dict[str, Any] = {
            "logGroupName": log_group_name,
            "logStreamName": log_stream_name,
            "limit": limit,
            "startFromHead": True,
        }
        if start_time:
            kwargs["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            kwargs["endTime"] = int(end_time.timestamp() * 1000)
        try:
            resp = self._logs.get_log_events(**kwargs)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code == "ResourceNotFoundException":
                raise ResourceNotFoundError("CloudWatch Log Stream", log_stream_name) from exc
            raise self._wrap_client_error(exc, "CloudWatch Logs get_log_events failed") from exc
        return resp.get("events", [])

    def filter_log_events(
        self,
        log_group_name: str,
        filter_pattern: str = "",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search across all log streams in a log group using a filter pattern."""
        kwargs: dict[str, Any] = {
            "logGroupName": log_group_name,
            "filterPattern": filter_pattern,
            "limit": limit,
        }
        if start_time:
            kwargs["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            kwargs["endTime"] = int(end_time.timestamp() * 1000)
        try:
            resp = self._logs.filter_log_events(**kwargs)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code == "ResourceNotFoundException":
                raise ResourceNotFoundError("CloudWatch Log Group", log_group_name) from exc
            raise self._wrap_client_error(exc, "CloudWatch Logs filter_log_events failed") from exc
        return resp.get("events", [])

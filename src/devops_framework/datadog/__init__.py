"""Datadog integration: logs and metrics."""

from devops_framework.datadog.logs import LogsClient
from devops_framework.datadog.metrics import MetricsClient

__all__ = ["LogsClient", "MetricsClient"]

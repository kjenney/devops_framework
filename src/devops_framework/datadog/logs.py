"""Datadog Logs client."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from datadog_api_client import ApiClient
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.logs_list_request import LogsListRequest
from datadog_api_client.v2.model.logs_list_request_page import LogsListRequestPage
from datadog_api_client.v2.model.logs_query_filter import LogsQueryFilter
from datadog_api_client.v2.model.logs_sort import LogsSort

from devops_framework.core.exceptions import DatadogAPIError
from devops_framework.datadog.base import DatadogBaseClient


class LogsClient(DatadogBaseClient):
    """Client for Datadog Logs API (v2)."""

    def search_logs(
        self,
        query: str = "*",
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        limit: int = 100,
        sort: str = "-timestamp",
    ) -> list[dict[str, Any]]:
        """
        Search Datadog logs.

        ``sort`` can be ``timestamp`` (ascending) or ``-timestamp`` (descending).
        """
        _sort = LogsSort.TIMESTAMP_DESCENDING if sort.startswith("-") else LogsSort.TIMESTAMP_ASCENDING

        query_filter = LogsQueryFilter(query=query)
        if from_time:
            query_filter["from"] = from_time.isoformat()
        if to_time:
            query_filter["to"] = to_time.isoformat()

        body = LogsListRequest(
            filter=query_filter,
            sort=_sort,
            page=LogsListRequestPage(limit=limit),
        )

        try:
            with ApiClient(self._dd_configuration) as client:
                api = LogsApi(client)
                resp = api.list_logs(body=body)
        except Exception as exc:
            raise DatadogAPIError(f"Datadog logs search failed: {exc}") from exc

        return [log.to_dict() for log in (resp.data or [])]

    def aggregate_logs(
        self,
        query: str = "*",
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        group_by_fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Aggregate logs using the Datadog Logs Aggregate API.

        Returns a list of bucket dicts.
        """
        from datadog_api_client.v2.api.logs_api import LogsApi
        from datadog_api_client.v2.model.logs_aggregate_request import LogsAggregateRequest
        from datadog_api_client.v2.model.logs_compute import LogsCompute
        from datadog_api_client.v2.model.logs_compute_type import LogsComputeType
        from datadog_api_client.v2.model.logs_group_by import LogsGroupBy

        compute = [LogsCompute(aggregation=LogsComputeType.COUNT, type=LogsComputeType.TOTAL)]
        group_bys = (
            [LogsGroupBy(facet=f) for f in group_by_fields] if group_by_fields else []
        )

        query_filter = LogsQueryFilter(query=query)
        if from_time:
            query_filter["from"] = from_time.isoformat()
        if to_time:
            query_filter["to"] = to_time.isoformat()

        body = LogsAggregateRequest(
            compute=compute,
            filter=query_filter,
            group_by=group_bys,
        )

        try:
            with ApiClient(self._dd_configuration) as client:
                api = LogsApi(client)
                resp = api.aggregate_logs(body=body)
        except Exception as exc:
            raise DatadogAPIError(f"Datadog logs aggregate failed: {exc}") from exc

        buckets = getattr(resp, "data", None)
        if buckets is None:
            return []
        buckets_obj = getattr(buckets, "buckets", [])
        return [b.to_dict() for b in (buckets_obj or [])]

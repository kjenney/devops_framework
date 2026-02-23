# Example: Query Datadog Logs & Metrics

This example shows how to search logs for errors, aggregate them by service, and correlate with CPU metrics.

## Prerequisites

```bash
export DD_API_KEY=your_api_key
export DD_APP_KEY=your_application_key
```

## Search Logs for Errors

```python
"""query_logs.py — Search and aggregate Datadog logs, then query related metrics."""

from datetime import datetime, timedelta, timezone
from devops_framework.datadog.logs import LogsClient
from devops_framework.datadog.metrics import MetricsClient

SERVICE = "my-api"
HOURS = 4

now = datetime.now(timezone.utc)
from_time = now - timedelta(hours=HOURS)


def search_errors(logs_client: LogsClient) -> list[dict]:
    """Return error logs from the last N hours."""
    logs = logs_client.search_logs(
        query=f"service:{SERVICE} status:error",
        from_time=from_time,
        to_time=now,
        limit=100,
    )
    print(f"\nFound {len(logs)} error log(s) in the last {HOURS} hours:\n")
    for log in logs[:10]:  # print first 10
        attrs = log.get("attributes", {})
        ts = attrs.get("timestamp", "")
        msg = attrs.get("message", "")
        host = attrs.get("host", "")
        print(f"  [{ts}] {host}: {msg[:120]}")
    return logs


def aggregate_by_status(logs_client: LogsClient) -> None:
    """Print error count grouped by HTTP status code."""
    buckets = logs_client.aggregate_logs(
        query=f"service:{SERVICE}",
        from_time=from_time,
        to_time=now,
        group_by_fields=["http.status_code"],
    )
    print(f"\nLog counts by HTTP status for {SERVICE}:")
    for bucket in buckets:
        by = bucket.get("by", {})
        computes = bucket.get("computes", {})
        print(f"  status={by.get('http.status_code', '?')}  count={computes.get('c0', 0)}")


def query_cpu(metrics_client: MetricsClient) -> None:
    """Print CPU utilization statistics for the same window."""
    result = metrics_client.query_metrics(
        query=f"avg:system.cpu.user{{service:{SERVICE}}}",
        from_time=from_time,
        to_time=now,
    )
    series = result.get("series", [])
    if not series:
        print("\nNo CPU metrics found.")
        return

    print(f"\nCPU utilization for {SERVICE} over the last {HOURS} hours:")
    for s in series:
        points = s.get("pointlist", [])
        if not points:
            continue
        values = [v for _, v in points if v is not None]
        if values:
            print(
                f"  scope={s.get('scope', '?')}  "
                f"min={min(values):.1f}%  "
                f"max={max(values):.1f}%  "
                f"avg={sum(values)/len(values):.1f}%"
            )


def main() -> None:
    logs_client = LogsClient()
    metrics_client = MetricsClient()

    search_errors(logs_client)
    aggregate_by_status(logs_client)
    query_cpu(metrics_client)


if __name__ == "__main__":
    main()
```

## Running the Script

```bash
python query_logs.py
```

## CLI Equivalents

```bash
# Search error logs
devops datadog search-logs --query "service:my-api status:error" --hours 4 --limit 100

# List active metrics
devops datadog list-metrics --hours 4

# Query CPU metrics
devops datadog query-metrics --query "avg:system.cpu.user{service:my-api}" --hours 4
```

## Tips

- Use `aggregate_logs` to count errors by facets like `service`, `status`, `http.status_code`, or `host` — much faster than iterating individual logs.
- The `query_metrics` response's `series[].pointlist` contains `[epoch_ms, value]` pairs.
- Datadog timestamps in log `attributes.timestamp` are ISO 8601 strings; parse them with `datetime.fromisoformat()` if you need arithmetic.

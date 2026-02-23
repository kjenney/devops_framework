# Datadog API Reference

Datadog clients require `DD_API_KEY` and `DD_APP_KEY` environment variables (or equivalent YAML config). Both clients extend `DatadogBaseClient`.

```python
from devops_framework.datadog.logs import LogsClient
from devops_framework.datadog.metrics import MetricsClient
```

---

## LogsClient

```python
LogsClient(config: Config | None = None)
```

Wraps the Datadog Logs API v2.

### Methods

#### `search_logs(query="*", from_time=None, to_time=None, limit=100, sort="-timestamp") -> list[dict]`

Search Datadog logs and return a list of log event dicts.

- `query` — Datadog log search query (default `"*"` matches all logs).
- `from_time` / `to_time` — `datetime` objects (timezone-aware recommended). Default to the last hour if omitted.
- `limit` — maximum number of results (default 100).
- `sort` — `"timestamp"` (ascending) or `"-timestamp"` (descending, default).

```python
from datetime import datetime, timedelta, timezone
from devops_framework.datadog.logs import LogsClient

client = LogsClient()
now = datetime.now(timezone.utc)

logs = client.search_logs(
    query="service:my-api status:error",
    from_time=now - timedelta(hours=4),
    to_time=now,
    limit=50,
)
for log in logs:
    attrs = log.get("attributes", {})
    print(attrs.get("timestamp"), attrs.get("message"))
```

#### `aggregate_logs(query="*", from_time=None, to_time=None, group_by_fields=None) -> list[dict]`

Aggregate logs using the Datadog Logs Aggregate API. Returns a list of bucket dicts.

- `group_by_fields` — list of facet names to group by (e.g. `["service", "status"]`).

```python
buckets = client.aggregate_logs(
    query="service:my-api",
    from_time=now - timedelta(hours=1),
    to_time=now,
    group_by_fields=["status"],
)
for bucket in buckets:
    print(bucket)
```

---

## MetricsClient

```python
MetricsClient(config: Config | None = None)
```

Wraps the Datadog Metrics API v1.

### Methods

#### `query_metrics(query, from_time=None, to_time=None) -> dict`

Query a Datadog metrics expression. Returns the raw API response dict (including `series`).

- `query` — Datadog metrics query string (e.g. `"avg:system.cpu.user{*}"`).
- `from_time` / `to_time` — `datetime` objects. Default to the last 1 hour.

```python
from devops_framework.datadog.metrics import MetricsClient

client = MetricsClient()
result = client.query_metrics(
    query="avg:system.cpu.user{host:web-01}",
    from_time=now - timedelta(hours=1),
    to_time=now,
)
for series in result.get("series", []):
    print(series["metric"], series["scope"])
    for ts, val in series.get("pointlist", []):
        print(f"  {ts}: {val:.2f}")
```

#### `list_active_metrics(from_time=None, host=None) -> list[str]`

Return a list of actively reporting metric names.

- `from_time` — look-back start time (default 24 hours ago).
- `host` — filter by reporting host.

```python
metrics = client.list_active_metrics(host="web-01")
print(metrics[:10])
```

#### `get_metric_metadata(metric_name) -> dict`

Return metadata (unit, description, type, etc.) for a specific metric.

```python
meta = client.get_metric_metadata("system.cpu.user")
print(meta.get("unit"), meta.get("description"))
```

# CLI Reference — Datadog

```
devops datadog [COMMAND] [OPTIONS]
```

Datadog commands require `DD_API_KEY` and `DD_APP_KEY` environment variables (or equivalent config).

---

## query-metrics

Query Datadog metrics and display a summary table.

```
devops datadog query-metrics [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--query` | `-q` | text | **required** | Datadog metrics query |
| `--hours` | | integer | `1` | Time window in hours |

**Examples**

```bash
# CPU utilization across all hosts for the last hour
devops datadog query-metrics --query "avg:system.cpu.user{*}"

# Memory usage on a specific host for the last 6 hours
devops datadog query-metrics --query "avg:system.mem.used{host:web-01}" --hours 6

# Request rate for a specific service
devops datadog query-metrics --query "sum:trace.web.request.hits{service:my-api}.as_rate()" --hours 2
```

---

## list-metrics

List actively reporting Datadog metrics.

```
devops datadog list-metrics [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--host` | | text | None | Filter metrics by reporting host |
| `--hours` | | integer | `24` | Look-back window in hours |

**Examples**

```bash
# All active metrics for the last 24 hours
devops datadog list-metrics

# Metrics reported by a specific host
devops datadog list-metrics --host web-01

# Metrics from the last hour
devops datadog list-metrics --hours 1
```

---

## search-logs

Search Datadog logs and print matching entries.

```
devops datadog search-logs [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--query` | `-q` | text | `*` | Datadog log search query |
| `--limit` | | integer | `20` | Maximum number of logs to return |
| `--hours` | | integer | `1` | Time window in hours |

**Examples**

```bash
# All logs for the last hour (up to 20)
devops datadog search-logs

# Error logs from a specific service
devops datadog search-logs --query "service:my-api status:error" --limit 50

# Search the last 4 hours
devops datadog search-logs --query "host:web-01 ERROR" --hours 4 --limit 100
```

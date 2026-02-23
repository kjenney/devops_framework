"""Datadog subcommand group for the `devops` CLI."""

from __future__ import annotations

import json
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from devops_framework.core.exceptions import DevOpsFrameworkError
from devops_framework.datadog.logs import LogsClient
from devops_framework.datadog.metrics import MetricsClient

app = typer.Typer(help="Datadog operations: logs and metrics.", no_args_is_help=True)
console = Console()
err_console = Console(stderr=True, style="bold red")


def _handle_error(exc: Exception) -> None:
    err_console.print(f"Error: {exc}")
    raise typer.Exit(code=1)


# ── Metrics ───────────────────────────────────────────────────────────────────

@app.command("query-metrics")
def query_metrics(
    query: str = typer.Option(..., "--query", "-q", help="Datadog metrics query (e.g. 'avg:system.cpu.user{*}')"),
    hours: int = typer.Option(1, "--hours", help="Time window in hours (default: 1)"),
) -> None:
    """Query Datadog metrics."""
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    from_time = now - timedelta(hours=hours)

    try:
        client = MetricsClient()
        result = client.query_metrics(query=query, from_time=from_time, to_time=now)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    series = result.get("series", [])
    if not series:
        console.print("[yellow]No data returned for the given query.[/yellow]")
        return

    table = Table(title=f"Metrics: {query}")
    table.add_column("Metric", style="cyan")
    table.add_column("Scope")
    table.add_column("Points")

    for s in series:
        table.add_row(
            s.get("metric", ""),
            s.get("scope", ""),
            str(len(s.get("pointlist", []))),
        )

    console.print(table)


@app.command("list-metrics")
def list_metrics(
    host: Optional[str] = typer.Option(None, "--host", help="Filter by host"),
    hours: int = typer.Option(24, "--hours", help="Look-back window in hours (default: 24)"),
) -> None:
    """List actively reporting Datadog metrics."""
    from datetime import datetime, timedelta, timezone

    from_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    try:
        client = MetricsClient()
        metrics = client.list_active_metrics(from_time=from_time, host=host)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title="Active Datadog Metrics")
    table.add_column("Metric Name", style="cyan")
    for name in metrics:
        table.add_row(name)

    console.print(table)


# ── Logs ──────────────────────────────────────────────────────────────────────

@app.command("search-logs")
def search_logs(
    query: str = typer.Option("*", "--query", "-q", help="Datadog log query"),
    limit: int = typer.Option(20, "--limit", help="Maximum number of logs to return"),
    hours: int = typer.Option(1, "--hours", help="Time window in hours (default: 1)"),
) -> None:
    """Search Datadog logs."""
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    from_time = now - timedelta(hours=hours)

    try:
        client = LogsClient()
        logs = client.search_logs(query=query, from_time=from_time, to_time=now, limit=limit)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    if not logs:
        console.print("[yellow]No logs found.[/yellow]")
        return

    for log in logs:
        attrs = log.get("attributes", {})
        ts = attrs.get("timestamp", "")
        message = attrs.get("message", json.dumps(attrs))
        status = attrs.get("status", "")
        host = attrs.get("host", "")
        console.print(f"[dim]{ts}[/dim] [{status}] [cyan]{host}[/cyan] {message}")

"""AWS subcommand group for the `devops` CLI."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from devops_framework.aws.cloudwatch import CloudWatchClient
from devops_framework.aws.ec2 import EC2Client
from devops_framework.aws.lambda_ import LambdaClient
from devops_framework.aws.rds import RDSClient
from devops_framework.core.exceptions import DevOpsFrameworkError

app = typer.Typer(help="AWS operations: EC2, RDS, Lambda, CloudWatch.", no_args_is_help=True)
console = Console()
err_console = Console(stderr=True, style="bold red")


def _handle_error(exc: Exception) -> None:
    err_console.print(f"Error: {exc}")
    raise typer.Exit(code=1)


# ── EC2 ───────────────────────────────────────────────────────────────────────

@app.command("list-instances")
def list_instances(
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    running_only: bool = typer.Option(False, "--running", help="Show only running instances"),
) -> None:
    """List EC2 instances."""
    try:
        client = EC2Client(region=region)
        instances = client.list_running_instances() if running_only else client.list_instances()
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title=f"EC2 Instances ({region or 'default region'})")
    table.add_column("Instance ID", style="cyan")
    table.add_column("State", style="green")
    table.add_column("Type")
    table.add_column("Private IP")
    table.add_column("Name")

    for inst in instances:
        name = next(
            (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
            "",
        )
        table.add_row(
            inst.get("InstanceId", ""),
            inst.get("State", {}).get("Name", ""),
            inst.get("InstanceType", ""),
            inst.get("PrivateIpAddress", ""),
            name,
        )

    console.print(table)


@app.command("describe-instance")
def describe_instance(
    instance_id: str = typer.Argument(..., help="EC2 instance ID"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
) -> None:
    """Describe a single EC2 instance."""
    try:
        client = EC2Client(region=region)
        inst = client.get_instance(instance_id)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    console.print_json(data=inst, default=str)


# ── RDS ───────────────────────────────────────────────────────────────────────

@app.command("list-db-instances")
def list_db_instances(
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
) -> None:
    """List RDS DB instances."""
    try:
        client = RDSClient(region=region)
        instances = client.list_instances()
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title="RDS DB Instances")
    table.add_column("Identifier", style="cyan")
    table.add_column("Engine")
    table.add_column("Status", style="green")
    table.add_column("Endpoint")
    table.add_column("Class")

    for inst in instances:
        endpoint = inst.get("Endpoint", {})
        ep_str = f"{endpoint.get('Address', '')}:{endpoint.get('Port', '')}" if endpoint else ""
        table.add_row(
            inst.get("DBInstanceIdentifier", ""),
            f"{inst.get('Engine', '')} {inst.get('EngineVersion', '')}",
            inst.get("DBInstanceStatus", ""),
            ep_str,
            inst.get("DBInstanceClass", ""),
        )

    console.print(table)


# ── Lambda ────────────────────────────────────────────────────────────────────

@app.command("list-functions")
def list_functions(
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
) -> None:
    """List Lambda functions."""
    try:
        client = LambdaClient(region=region)
        functions = client.list_functions()
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title="Lambda Functions")
    table.add_column("Name", style="cyan")
    table.add_column("Runtime")
    table.add_column("Memory (MB)")
    table.add_column("Timeout (s)")
    table.add_column("Last Modified")

    for fn in functions:
        table.add_row(
            fn.get("FunctionName", ""),
            fn.get("Runtime", ""),
            str(fn.get("MemorySize", "")),
            str(fn.get("Timeout", "")),
            fn.get("LastModified", ""),
        )

    console.print(table)


@app.command("invoke-function")
def invoke_function(
    function_name: str = typer.Argument(..., help="Lambda function name or ARN"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    payload: Optional[str] = typer.Option(None, "--payload", help="JSON payload string"),
) -> None:
    """Invoke a Lambda function synchronously."""
    import json

    parsed_payload = None
    if payload:
        try:
            parsed_payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            err_console.print(f"Invalid JSON payload: {exc}")
            raise typer.Exit(code=1)

    try:
        client = LambdaClient(region=region)
        result = client.invoke(function_name, payload=parsed_payload)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    console.print_json(data=result, default=str)


# ── CloudWatch ────────────────────────────────────────────────────────────────

@app.command("list-log-groups")
def list_log_groups(
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    prefix: Optional[str] = typer.Option(None, "--prefix", help="Log group name prefix filter"),
) -> None:
    """List CloudWatch Log groups."""
    try:
        client = CloudWatchClient(region=region)
        groups = client.list_log_groups(prefix=prefix)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title="CloudWatch Log Groups")
    table.add_column("Name", style="cyan")
    table.add_column("Retention (days)")
    table.add_column("Stored Bytes")

    for g in groups:
        table.add_row(
            g.get("logGroupName", ""),
            str(g.get("retentionInDays", "Never expire")),
            str(g.get("storedBytes", 0)),
        )

    console.print(table)

"""EKS subcommand group for the `devops` CLI."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from devops_framework.core.exceptions import DevOpsFrameworkError
from devops_framework.eks.clusters import ClusterClient
from devops_framework.eks.deployments import DeploymentClient
from devops_framework.eks.pods import PodClient
from devops_framework.eks.services import ServiceClient

app = typer.Typer(help="EKS operations: clusters, pods, deployments, services.", no_args_is_help=True)
console = Console()
err_console = Console(stderr=True, style="bold red")


def _handle_error(exc: Exception) -> None:
    err_console.print(f"Error: {exc}")
    raise typer.Exit(code=1)


# ── Clusters ───────────────────────────────────────────────────────────────────

@app.command("list-clusters")
def list_clusters(
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
) -> None:
    """List all EKS clusters in the AWS account."""
    try:
        client = ClusterClient(region=region, profile=profile)
        clusters = client.list_clusters()
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title="EKS Clusters")
    table.add_column("Cluster Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Kubernetes Version")
    table.add_column("Endpoint")
    table.add_column("Created")

    for cluster in clusters:
        table.add_row(
            cluster.get("name", ""),
            cluster.get("status", ""),
            cluster.get("version", ""),
            cluster.get("endpoint", ""),
            str(cluster.get("createdAt", "")),
        )

    console.print(table)


# ── Pods ──────────────────────────────────────────────────────────────────────

@app.command("list-pods")
def list_pods(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    label_selector: Optional[str] = typer.Option(None, "--selector", "-l", help="Label selector"),
) -> None:
    """List pods in a namespace."""
    try:
        client = PodClient(namespace=namespace)
        pods = client.list_pods(label_selector=label_selector)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title=f"Pods in namespace '{namespace}'")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Ready")
    table.add_column("Restarts")
    table.add_column("Node")

    for pod in pods:
        meta = pod.metadata
        status = pod.status
        phase = status.phase if status else "Unknown"
        node = spec.node_name if (spec := pod.spec) else ""

        containers = (status.container_statuses or []) if status else []
        ready_count = sum(1 for c in containers if c.ready)
        restarts = sum(c.restart_count for c in containers)

        table.add_row(
            meta.name if meta else "",
            phase or "",
            f"{ready_count}/{len(containers)}",
            str(restarts),
            node or "",
        )

    console.print(table)


@app.command("get-pod-logs")
def get_pod_logs(
    pod_name: str = typer.Argument(..., help="Pod name"),
    namespace: str = typer.Option("default", "--namespace", "-n"),
    container: Optional[str] = typer.Option(None, "--container", "-c", help="Container name"),
    tail: int = typer.Option(100, "--tail", help="Number of lines to show"),
    previous: bool = typer.Option(False, "--previous", help="Show logs from previous container instance"),
) -> None:
    """Stream logs from a pod container."""
    try:
        client = PodClient(namespace=namespace)
        logs = client.get_pod_logs(pod_name, container=container, tail_lines=tail, previous=previous)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    console.print(logs)


# ── Deployments ───────────────────────────────────────────────────────────────

@app.command("list-deployments")
def list_deployments(
    namespace: str = typer.Option("default", "--namespace", "-n"),
) -> None:
    """List deployments in a namespace."""
    try:
        client = DeploymentClient(namespace=namespace)
        deployments = client.list_deployments()
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title=f"Deployments in namespace '{namespace}'")
    table.add_column("Name", style="cyan")
    table.add_column("Ready")
    table.add_column("Up-to-date")
    table.add_column("Available")

    for dep in deployments:
        meta = dep.metadata
        status = dep.status
        spec = dep.spec
        desired = spec.replicas if spec else 0
        ready = status.ready_replicas or 0 if status else 0
        updated = status.updated_replicas or 0 if status else 0
        available = status.available_replicas or 0 if status else 0

        table.add_row(
            meta.name if meta else "",
            f"{ready}/{desired}",
            str(updated),
            str(available),
        )

    console.print(table)


@app.command("scale-deployment")
def scale_deployment(
    deployment_name: str = typer.Argument(..., help="Deployment name"),
    replicas: int = typer.Argument(..., help="Desired replica count"),
    namespace: str = typer.Option("default", "--namespace", "-n"),
) -> None:
    """Scale a deployment to the specified replica count."""
    try:
        client = DeploymentClient(namespace=namespace)
        client.scale_deployment(deployment_name, replicas=replicas)
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    console.print(f"[green]Scaled {deployment_name!r} to {replicas} replicas.[/green]")


# ── Services ──────────────────────────────────────────────────────────────────

@app.command("list-services")
def list_services(
    namespace: str = typer.Option("default", "--namespace", "-n"),
) -> None:
    """List services in a namespace."""
    try:
        client = ServiceClient(namespace=namespace)
        services = client.list_services()
    except DevOpsFrameworkError as exc:
        _handle_error(exc)
        return

    table = Table(title=f"Services in namespace '{namespace}'")
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Cluster IP")
    table.add_column("External IP")
    table.add_column("Ports")

    for svc in services:
        meta = svc.metadata
        spec = svc.spec
        svc_type = spec.type if spec else ""
        cluster_ip = spec.cluster_ip if spec else ""
        ports_str = (
            ", ".join(
                f"{p.port}/{p.protocol}" for p in (spec.ports or [])
            )
            if spec
            else ""
        )
        external_ips = (
            ", ".join(spec.external_i_ps or []) if spec and spec.external_i_ps else ""
        )

        table.add_row(
            meta.name if meta else "",
            svc_type or "",
            cluster_ip or "",
            external_ips,
            ports_str,
        )

    console.print(table)

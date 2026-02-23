"""Root Typer application — entry point for the `devops` CLI."""

from __future__ import annotations

import typer

from devops_framework.cli import aws as aws_cli
from devops_framework.cli import datadog as datadog_cli
from devops_framework.cli import eks as eks_cli

app = typer.Typer(
    name="devops",
    help="DevOps Framework CLI — troubleshoot AWS, EKS, and Datadog.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

app.add_typer(aws_cli.app, name="aws")
app.add_typer(eks_cli.app, name="eks")
app.add_typer(datadog_cli.app, name="datadog")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

# DevOps Framework

A Python library and CLI for DevOps troubleshooting across **AWS**, **EKS/Kubernetes**, and **Datadog**.

## Features

- **AWS** — EC2, RDS, Lambda, and CloudWatch operations
- **EKS** — Pod, Deployment, and Service management via kubeconfig
- **Datadog** — Log search and metrics querying
- **Unified CLI** — `devops aws | eks | datadog` subcommands
- **Consistent error handling** — custom exception hierarchy wrapping all third-party errors

## Quick Install

```bash
pip install devops-framework
```

## Minimal Example

```python
from devops_framework.aws.ec2 import EC2Client

client = EC2Client(region="us-east-1")
instances = client.list_running_instances()
for inst in instances:
    print(inst["InstanceId"], inst["State"]["Name"])
```

## CLI Quick-Start

```bash
# List running EC2 instances
devops aws list-instances --region us-east-1 --running

# Stream pod logs
devops eks get-pod-logs my-pod-abc123 --namespace production --tail 50

# Query Datadog metrics for the last 2 hours
devops datadog query-metrics --query "avg:system.cpu.user{*}" --hours 2
```

## Navigation

| Section | Description |
|---|---|
| [Installation](installation.md) | Set up a virtual environment and install the package |
| [Configuration](configuration.md) | Env vars, YAML config, and precedence rules |
| [CLI Reference](cli/aws.md) | All `devops` subcommands with options and examples |
| [API Reference](api/core.md) | Python client classes and methods |
| [Examples](examples/troubleshoot-ec2.md) | End-to-end scripts for common tasks |

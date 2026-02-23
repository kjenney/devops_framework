# Example: Troubleshoot EC2 Instances

This example shows how to find unhealthy instances, inspect their status, and restart them.

## Scenario

You have a fleet of EC2 instances and want to:

1. List all instances with a failed status check
2. Inspect each unhealthy instance
3. Stop and restart instances that have failed

## Script

```python
"""troubleshoot_ec2.py — Find and restart EC2 instances with failed status checks."""

from devops_framework.aws.ec2 import EC2Client
from devops_framework.core.exceptions import AWSAPIError, ResourceNotFoundError

REGION = "us-east-1"


def find_unhealthy_instances(client: EC2Client) -> list[dict]:
    """Return instances with a failed instance or system status check."""
    all_instances = client.list_running_instances()
    unhealthy = []

    for inst in all_instances:
        instance_id = inst["InstanceId"]
        try:
            status = client.get_instance_status(instance_id)
        except ResourceNotFoundError:
            continue

        instance_check = status.get("InstanceStatus", {}).get("Status", "ok")
        system_check = status.get("SystemStatus", {}).get("Status", "ok")

        if instance_check != "ok" or system_check != "ok":
            unhealthy.append({
                "instance_id": instance_id,
                "instance_check": instance_check,
                "system_check": system_check,
                "name": next(
                    (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
                    "(no name)",
                ),
            })

    return unhealthy


def restart_instance(client: EC2Client, instance_id: str) -> None:
    """Stop then start an EC2 instance."""
    print(f"  Stopping {instance_id}...")
    try:
        client.stop_instance(instance_id)
        print(f"  Starting {instance_id}...")
        client.start_instance(instance_id)
        print(f"  {instance_id} restarted successfully.")
    except AWSAPIError as exc:
        print(f"  Failed to restart {instance_id}: {exc}")


def main() -> None:
    client = EC2Client(region=REGION)
    print(f"Scanning instances in {REGION}...")

    unhealthy = find_unhealthy_instances(client)

    if not unhealthy:
        print("All instances are healthy.")
        return

    print(f"\nFound {len(unhealthy)} unhealthy instance(s):\n")
    for info in unhealthy:
        print(
            f"  {info['instance_id']} ({info['name']}) — "
            f"instance={info['instance_check']}, system={info['system_check']}"
        )

    print("\nRestarting unhealthy instances...")
    for info in unhealthy:
        restart_instance(client, info["instance_id"])


if __name__ == "__main__":
    main()
```

## Running the Script

```bash
# Set AWS credentials
export AWS_DEFAULT_REGION=us-east-1
export AWS_PROFILE=my-profile   # or use AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY

python troubleshoot_ec2.py
```

## Using the CLI Instead

```bash
# Check for instances with non-running states
devops aws list-instances --region us-east-1

# Inspect a specific instance
devops aws describe-instance i-0abc123def456 --region us-east-1
```

## Tips

- `get_instance_status` checks both **instance status** (OS-level) and **system status** (hardware-level).
- Status values are `ok`, `impaired`, `insufficient-data`, `not-applicable`, or `initializing`.
- Always check that `instance_check != "ok"` **or** `system_check != "ok"` — either check failing indicates a problem.

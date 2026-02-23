# Example: Manage Kubernetes Deployments

This example covers inspecting pods, streaming logs, scaling deployments, and triggering rolling restarts.

## Prerequisites

- A valid kubeconfig file (e.g. `~/.kube/config` or pointed to by `KUBECONFIG`)
- Cluster access for the target namespace

## Scenario

Your `production` namespace has a service called `my-api`. You need to:

1. Check pod health
2. Stream logs from a failing pod
3. Scale the deployment
4. Trigger a rolling restart

## Python Script

```python
"""manage_deployments.py — Inspect and manage a Kubernetes deployment."""

from devops_framework.eks.deployments import DeploymentClient
from devops_framework.eks.pods import PodClient
from devops_framework.core.exceptions import KubernetesAPIError, ResourceNotFoundError

NAMESPACE = "production"
DEPLOYMENT = "my-api"


def check_pods(pod_client: PodClient) -> None:
    """Print pod health summary."""
    pods = pod_client.list_pods(label_selector=f"app={DEPLOYMENT}")
    print(f"\nPods for {DEPLOYMENT} in {NAMESPACE}:")
    for pod in pods:
        meta = pod.metadata
        status = pod.status
        containers = (status.container_statuses or []) if status else []
        ready = sum(1 for c in containers if c.ready)
        restarts = sum(c.restart_count for c in containers)
        print(
            f"  {meta.name}  phase={status.phase}  "
            f"ready={ready}/{len(containers)}  restarts={restarts}"
        )
    return pods


def stream_logs_for_crashlooping(pod_client: PodClient, pods: list) -> None:
    """Print the previous container logs for any pod with high restart count."""
    for pod in pods:
        containers = (pod.status.container_statuses or []) if pod.status else []
        restarts = sum(c.restart_count for c in containers)
        if restarts > 5:
            print(f"\nLogs (previous) for {pod.metadata.name}:")
            try:
                logs = pod_client.get_pod_logs(
                    pod.metadata.name, tail_lines=50, previous=True
                )
                print(logs)
            except ResourceNotFoundError:
                print("  Pod not found (may have been deleted).")


def main() -> None:
    pod_client = PodClient(namespace=NAMESPACE)
    dep_client = DeploymentClient(namespace=NAMESPACE)

    pods = check_pods(pod_client)
    stream_logs_for_crashlooping(pod_client, pods)

    # Scale up if fewer than 3 replicas are ready
    dep = dep_client.get_deployment(DEPLOYMENT)
    ready = dep.status.ready_replicas or 0 if dep.status else 0
    if ready < 3:
        print(f"\nOnly {ready} replicas ready. Scaling {DEPLOYMENT} to 3...")
        dep_client.scale_deployment(DEPLOYMENT, replicas=3)

    # Trigger a rolling restart
    print(f"\nTriggering rolling restart of {DEPLOYMENT}...")
    dep_client.restart_deployment(DEPLOYMENT)
    print("Rolling restart initiated.")


if __name__ == "__main__":
    main()
```

## Running the Script

```bash
export KUBECONFIG=~/.kube/config
export KUBE_CONTEXT=my-eks-cluster   # optional, uses current context by default

python manage_deployments.py
```

## CLI Equivalents

```bash
# Check pods
devops eks list-pods --namespace production --selector app=my-api

# Stream logs from a specific pod
devops eks get-pod-logs my-api-abc123 --namespace production --tail 100

# Stream previous container logs
devops eks get-pod-logs my-api-abc123 --namespace production --previous

# Check deployment status
devops eks list-deployments --namespace production

# Scale the deployment
devops eks scale-deployment my-api 5 --namespace production
```

## Tips

- `restart_deployment` patches a pod template annotation — Kubernetes rolls pods one at a time while keeping others available.
- Use `delete_pod` on a specific pod to force an immediate restart of that pod (the Deployment controller will recreate it).
- Combine `--selector` filtering with `list_pods` to target only the pods belonging to a specific deployment.

# EKS API Reference

EKS clients authenticate via kubeconfig (file path from `KUBECONFIG` env var or config YAML). All three clients extend `EKSBaseClient`.

```python
from devops_framework.eks.pods import PodClient
from devops_framework.eks.deployments import DeploymentClient
from devops_framework.eks.services import ServiceClient
```

---

## PodClient

```python
PodClient(namespace: str = "default", config: Config | None = None)
```

### Methods

#### `list_pods(namespace=None, label_selector=None) -> list[V1Pod]`

List pods. Uses the client's default namespace if `namespace` is omitted.

```python
client = PodClient(namespace="production")

# All pods in namespace
pods = client.list_pods()

# Filter by label
pods = client.list_pods(label_selector="app=my-service,env=prod")
```

#### `get_pod(pod_name, namespace=None) -> V1Pod`

Return a single pod object. Raises `ResourceNotFoundError` (HTTP 404) if not found.

#### `get_pod_logs(pod_name, namespace=None, container=None, tail_lines=100, previous=False) -> str`

Return log output from a pod container as a string.

- `container` — specify a container name in multi-container pods.
- `tail_lines` — number of lines from the end of the log.
- `previous` — retrieve logs from the previous (crashed) container instance.

```python
logs = client.get_pod_logs(
    "my-pod-abc123",
    container="app",
    tail_lines=200,
    previous=True,
)
print(logs)
```

#### `delete_pod(pod_name, namespace=None) -> None`

Delete a pod. If the pod is managed by a controller (Deployment, ReplicaSet, etc.), it will be recreated automatically.

---

## DeploymentClient

```python
DeploymentClient(namespace: str = "default", config: Config | None = None)
```

### Methods

#### `list_deployments(namespace=None, label_selector=None) -> list[V1Deployment]`

List deployments in the given namespace.

#### `get_deployment(deployment_name, namespace=None) -> V1Deployment`

Return a single deployment. Raises `ResourceNotFoundError` if not found.

#### `scale_deployment(deployment_name, replicas, namespace=None) -> V1Deployment`

Patch the deployment's replica count. Returns the updated `V1Deployment` object.

```python
client = DeploymentClient(namespace="production")
client.scale_deployment("my-api", replicas=5)
```

#### `restart_deployment(deployment_name, namespace=None) -> V1Deployment`

Trigger a rolling restart by patching the pod template annotation `kubectl.kubernetes.io/restartedAt`. Equivalent to `kubectl rollout restart deployment/<name>`.

```python
client.restart_deployment("my-api")
```

---

## ServiceClient

```python
ServiceClient(namespace: str = "default", config: Config | None = None)
```

### Methods

#### `list_services(namespace=None, label_selector=None) -> list[V1Service]`

List services in the given namespace.

#### `get_service(service_name, namespace=None) -> V1Service`

Return a single service. Raises `ResourceNotFoundError` if not found.

#### `get_endpoints(service_name, namespace=None) -> V1Endpoints`

Return the `Endpoints` object for a service. Useful for checking which pod IPs back a service.

```python
client = ServiceClient(namespace="production")
ep = client.get_endpoints("my-api")
for subset in ep.subsets or []:
    for addr in subset.addresses or []:
        print(addr.ip, addr.target_ref.name)
```

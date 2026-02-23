# CLI Reference — EKS

```
devops eks [COMMAND] [OPTIONS]
```

All EKS commands use the kubeconfig resolved from `KUBECONFIG` env var or `~/.devops-framework/config.yaml`. The default namespace is `default` unless overridden with `--namespace`.

---

## list-pods

List pods in a namespace.

```
devops eks list-pods [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--namespace` | `-n` | text | `default` | Kubernetes namespace |
| `--selector` | `-l` | text | None | Label selector (e.g. `app=my-api`) |

**Examples**

```bash
# Pods in the default namespace
devops eks list-pods

# Pods in a specific namespace
devops eks list-pods --namespace production

# Filter by label
devops eks list-pods --namespace production --selector app=my-api,env=prod
```

---

## get-pod-logs

Stream logs from a pod container.

```
devops eks get-pod-logs POD_NAME [OPTIONS]
```

| Argument | Description |
|---|---|
| `POD_NAME` | Name of the pod |

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--namespace` | `-n` | text | `default` | Kubernetes namespace |
| `--container` | `-c` | text | None | Container name (multi-container pods) |
| `--tail` | | integer | `100` | Number of log lines to show |
| `--previous` | | flag | false | Show logs from the previous crashed container |

**Examples**

```bash
# Last 100 lines from a pod
devops eks get-pod-logs my-pod-abc123

# Last 200 lines from a specific container
devops eks get-pod-logs my-pod-abc123 --namespace production --container app --tail 200

# Logs from the previous (crashed) container instance
devops eks get-pod-logs my-pod-abc123 --previous
```

---

## list-deployments

List deployments in a namespace.

```
devops eks list-deployments [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--namespace` | `-n` | text | `default` | Kubernetes namespace |

**Examples**

```bash
devops eks list-deployments
devops eks list-deployments --namespace staging
```

---

## scale-deployment

Scale a deployment to the specified replica count.

```
devops eks scale-deployment DEPLOYMENT_NAME REPLICAS [OPTIONS]
```

| Argument | Description |
|---|---|
| `DEPLOYMENT_NAME` | Name of the deployment |
| `REPLICAS` | Desired replica count |

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--namespace` | `-n` | text | `default` | Kubernetes namespace |

**Examples**

```bash
# Scale to 5 replicas in the default namespace
devops eks scale-deployment my-api 5

# Scale down to 0 (stop all pods)
devops eks scale-deployment my-api 0 --namespace production

# Scale up
devops eks scale-deployment my-api 10 --namespace production
```

---

## list-services

List services in a namespace.

```
devops eks list-services [OPTIONS]
```

| Option | Short | Type | Default | Description |
|---|---|---|---|---|
| `--namespace` | `-n` | text | `default` | Kubernetes namespace |

**Examples**

```bash
devops eks list-services
devops eks list-services --namespace production
```

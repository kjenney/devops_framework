# Core API Reference

The `devops_framework.core` package provides the shared foundation used by all integration clients.

## Config

```python
from devops_framework.core.config import Config
```

Unified configuration holder. Resolves settings from environment variables, a YAML file, or built-in defaults.

### Constructor

```python
Config(config_path: Path | None = None)
```

- `config_path` — override the default config path (`~/.devops-framework/config.yaml`).

### Properties

| Property | Type | Description |
|---|---|---|
| `aws_region` | `str` | AWS region (default: `us-east-1`) |
| `aws_profile` | `str \| None` | Named AWS credentials profile |
| `aws_role_arn` | `str \| None` | IAM role ARN to assume |
| `eks_kubeconfig` | `str \| None` | Path to kubeconfig file |
| `eks_context` | `str \| None` | Kubeconfig context name |
| `eks_namespace` | `str` | Default Kubernetes namespace (default: `default`) |
| `datadog_api_key` | `str \| None` | Datadog API key |
| `datadog_app_key` | `str \| None` | Datadog application key |
| `datadog_site` | `str` | Datadog site (default: `datadoghq.com`) |

### Methods

#### `require(*attr_names)`

Raise `ConfigurationError` if any listed attribute is `None` or empty.

```python
cfg = Config()
cfg.require("datadog_api_key", "datadog_app_key")
```

---

## IntegrationBaseClient

```python
from devops_framework.core.base import IntegrationBaseClient
```

Abstract base class for all integration clients. Provides a shared `Config` instance and a module-scoped logger.

### Constructor

```python
IntegrationBaseClient(config: Config | None = None)
```

A fresh `Config()` is created automatically if `config` is not supplied.

### Properties

| Property | Type | Description |
|---|---|---|
| `config` | `Config` | The resolved configuration object |
| `logger` | `logging.Logger` | Logger scoped to the subclass module |

### Abstract Methods

#### `health_check() -> bool`

Must be implemented by each subclass. Return `True` if the integration is reachable and authenticated.

---

## Exception Hierarchy

All exceptions inherit from `DevOpsFrameworkError`.

```python
from devops_framework.core.exceptions import (
    DevOpsFrameworkError,
    AuthenticationError,
    AWSAuthError,
    DatadogAuthError,
    EKSAuthError,
    ResourceNotFoundError,
    IntegrationAPIError,
    AWSAPIError,
    DatadogAPIError,
    KubernetesAPIError,
    ConfigurationError,
)
```

```
DevOpsFrameworkError
├── AuthenticationError
│   ├── AWSAuthError
│   ├── DatadogAuthError
│   └── EKSAuthError
├── ResourceNotFoundError
├── IntegrationAPIError
│   ├── AWSAPIError
│   ├── DatadogAPIError
│   └── KubernetesAPIError
└── ConfigurationError
```

### DevOpsFrameworkError

Base exception. All framework errors carry a `message` string and optional `details` dict.

```python
try:
    ...
except DevOpsFrameworkError as exc:
    print(exc.message)
    print(exc.details)
```

### ResourceNotFoundError

Raised when a requested resource does not exist.

```python
from devops_framework.core.exceptions import ResourceNotFoundError

try:
    client.get_instance("i-nonexistent")
except ResourceNotFoundError as exc:
    print(exc.resource_type)   # "EC2 Instance"
    print(exc.identifier)      # "i-nonexistent"
```

### IntegrationAPIError

Raised when an API call fails. Includes an optional `status_code`.

```python
except IntegrationAPIError as exc:
    print(exc.status_code)
```

### ConfigurationError

Raised when required configuration is missing or the YAML config cannot be parsed.

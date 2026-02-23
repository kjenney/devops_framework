# Configuration

The framework resolves configuration in this order of precedence (highest first):

1. **Environment variables**
2. **YAML config file** (`~/.devops-framework/config.yaml`)
3. **Built-in defaults**

## Environment Variables

### AWS

| Variable | Config property | Default | Description |
|---|---|---|---|
| `AWS_DEFAULT_REGION` or `AWS_REGION` | `aws_region` | `us-east-1` | AWS region |
| `AWS_PROFILE` | `aws_profile` | None | Named AWS credentials profile |
| `AWS_ROLE_ARN` | `aws_role_arn` | None | IAM role to assume |

Standard boto3 credential vars (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) are also supported and resolved by boto3 automatically.

### EKS / Kubernetes

| Variable | Config property | Default | Description |
|---|---|---|---|
| `KUBECONFIG` | `eks_kubeconfig` | None | Path to kubeconfig file |
| `KUBE_CONTEXT` | `eks_context` | None | Kubeconfig context to use |
| `KUBE_NAMESPACE` | `eks_namespace` | `default` | Default Kubernetes namespace |

### Datadog

| Variable | Config property | Default | Description |
|---|---|---|---|
| `DD_API_KEY` | `datadog_api_key` | **required** | Datadog API key |
| `DD_APP_KEY` | `datadog_app_key` | **required** | Datadog application key |
| `DD_SITE` | `datadog_site` | `datadoghq.com` | Datadog site (e.g. `datadoghq.eu`) |

## YAML Config File

Place a YAML file at `~/.devops-framework/config.yaml`:

```yaml
aws:
  region: us-west-2
  profile: my-aws-profile
  # role_arn: arn:aws:iam::123456789012:role/MyRole

eks:
  kubeconfig: /home/user/.kube/config
  context: my-eks-cluster
  namespace: production

datadog:
  api_key: YOUR_DD_API_KEY
  app_key: YOUR_DD_APP_KEY
  site: datadoghq.com
```

!!! warning
    Avoid storing API keys in plain text. Prefer environment variables or a secrets manager.

## Using the Config Object Directly

```python
from devops_framework.core.config import Config

cfg = Config()
print(cfg.aws_region)       # e.g. "us-west-2"
print(cfg.eks_namespace)    # e.g. "production"
print(cfg.datadog_site)     # e.g. "datadoghq.com"

# Raise ConfigurationError if a required key is missing
cfg.require("datadog_api_key", "datadog_app_key")
```

## Custom Config Path

All clients accept an optional `config` parameter:

```python
from pathlib import Path
from devops_framework.core.config import Config
from devops_framework.aws.ec2 import EC2Client

cfg = Config(config_path=Path("/etc/myapp/devops.yaml"))
client = EC2Client(config=cfg)
```

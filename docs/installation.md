# Installation

## Requirements

- Python 3.12+
- AWS credentials configured (for AWS commands)
- A valid kubeconfig (for EKS commands)
- Datadog API and application keys (for Datadog commands)

## Install from Source

```bash
# Clone the repository
git clone https://github.com/kjenney/devops_framework.git
cd devops-framework

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

## Install from PyPI

```bash
pip install devops-framework
```

## Verify the Installation

```bash
devops --help
```

Expected output:

```
Usage: devops [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  aws      AWS operations: EC2, RDS, Lambda, CloudWatch.
  eks      EKS/Kubernetes operations: pods, deployments, services.
  datadog  Datadog operations: logs and metrics.
```

## Running Tests

```bash
# All tests with coverage
pytest

# Fast (no coverage)
pytest --no-cov

# Verbose
pytest -v
```

Or use the Makefile shortcuts:

```bash
make test
make test-fast
make test-verbose
```

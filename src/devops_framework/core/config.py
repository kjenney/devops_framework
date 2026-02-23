"""Configuration loader: env vars → YAML file → defaults."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from devops_framework.core.exceptions import ConfigurationError

_DEFAULT_CONFIG_PATH = Path.home() / ".devops-framework" / "config.yaml"


def _deep_get(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Traverse nested dict with a list of keys, returning default if missing."""
    node = mapping
    for key in keys:
        if not isinstance(node, dict):
            return default
        node = node.get(key, default)
        if node is default:
            return default
    return node


class Config:
    """
    Unified configuration holder.

    Priority: environment variables > YAML config file > defaults.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        self._yaml: dict[str, Any] = {}
        path = config_path or _DEFAULT_CONFIG_PATH
        if path.exists():
            try:
                with path.open() as fh:
                    data = yaml.safe_load(fh)
                if data and isinstance(data, dict):
                    self._yaml = data
            except yaml.YAMLError as exc:
                raise ConfigurationError(f"Failed to parse config file {path}: {exc}") from exc

    # ── AWS ───────────────────────────────────────────────────────────────────

    @property
    def aws_region(self) -> str:
        return (
            os.environ.get("AWS_DEFAULT_REGION")
            or os.environ.get("AWS_REGION")
            or _deep_get(self._yaml, "aws", "region")
            or "us-east-1"
        )

    @property
    def aws_profile(self) -> str | None:
        return os.environ.get("AWS_PROFILE") or _deep_get(self._yaml, "aws", "profile")

    @property
    def aws_role_arn(self) -> str | None:
        return os.environ.get("AWS_ROLE_ARN") or _deep_get(self._yaml, "aws", "role_arn")

    # ── EKS / Kubernetes ──────────────────────────────────────────────────────

    @property
    def eks_kubeconfig(self) -> str | None:
        return os.environ.get("KUBECONFIG") or _deep_get(self._yaml, "eks", "kubeconfig")

    @property
    def eks_context(self) -> str | None:
        return os.environ.get("KUBE_CONTEXT") or _deep_get(self._yaml, "eks", "context")

    @property
    def eks_namespace(self) -> str:
        return (
            os.environ.get("KUBE_NAMESPACE")
            or _deep_get(self._yaml, "eks", "namespace")
            or "default"
        )

    # ── Datadog ───────────────────────────────────────────────────────────────

    @property
    def datadog_api_key(self) -> str | None:
        return os.environ.get("DD_API_KEY") or _deep_get(self._yaml, "datadog", "api_key")

    @property
    def datadog_app_key(self) -> str | None:
        return os.environ.get("DD_APP_KEY") or _deep_get(self._yaml, "datadog", "app_key")

    @property
    def datadog_site(self) -> str:
        return (
            os.environ.get("DD_SITE")
            or _deep_get(self._yaml, "datadog", "site")
            or "datadoghq.com"
        )

    def require(self, *attr_names: str) -> None:
        """Raise ConfigurationError if any listed config attribute is None/empty."""
        for name in attr_names:
            value = getattr(self, name, None)
            if not value:
                raise ConfigurationError(
                    f"Required configuration '{name}' is not set. "
                    "Set the corresponding environment variable or add it to your config.yaml."
                )

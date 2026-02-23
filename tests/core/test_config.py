"""Tests for core/config.py."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from devops_framework.core.config import Config
from devops_framework.core.exceptions import ConfigurationError


def test_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Config returns sensible defaults when nothing is configured."""
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    cfg = Config(config_path=tmp_path / "nonexistent.yaml")
    assert cfg.aws_region == "us-east-1"
    assert cfg.eks_namespace == "default"
    assert cfg.datadog_site == "datadoghq.com"


def test_env_vars_take_priority(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Environment variables override YAML file values."""
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(yaml.dump({"aws": {"region": "eu-west-1"}}))

    monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-southeast-1")
    cfg = Config(config_path=yaml_path)
    assert cfg.aws_region == "ap-southeast-1"


def test_yaml_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """YAML config is used when env vars are absent."""
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)

    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(yaml.dump({"aws": {"region": "ca-central-1"}}))
    cfg = Config(config_path=yaml_path)
    assert cfg.aws_region == "ca-central-1"


def test_datadog_keys_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DD_API_KEY", "my-api-key")
    monkeypatch.setenv("DD_APP_KEY", "my-app-key")
    cfg = Config(config_path=tmp_path / "nonexistent.yaml")
    assert cfg.datadog_api_key == "my-api-key"
    assert cfg.datadog_app_key == "my-app-key"


def test_datadog_keys_from_yaml(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("DD_API_KEY", raising=False)
    monkeypatch.delenv("DD_APP_KEY", raising=False)
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(yaml.dump({"datadog": {"api_key": "yaml-key", "app_key": "yaml-app"}}))
    cfg = Config(config_path=yaml_path)
    assert cfg.datadog_api_key == "yaml-key"
    assert cfg.datadog_app_key == "yaml-app"


def test_invalid_yaml_raises(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "config.yaml"
    bad_yaml.write_text("key: [unclosed")
    with pytest.raises(ConfigurationError, match="Failed to parse config file"):
        Config(config_path=bad_yaml)


def test_require_raises_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DD_API_KEY", raising=False)
    cfg = Config(config_path=tmp_path / "nonexistent.yaml")
    with pytest.raises(ConfigurationError, match="datadog_api_key"):
        cfg.require("datadog_api_key")


def test_require_passes_when_set(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DD_API_KEY", "key")
    cfg = Config(config_path=tmp_path / "nonexistent.yaml")
    cfg.require("datadog_api_key")  # should not raise

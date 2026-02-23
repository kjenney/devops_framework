"""Tests for cli/aws.py using Typer's CliRunner and mocked clients."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from devops_framework.cli.main import app

runner = CliRunner()


def test_aws_help() -> None:
    result = runner.invoke(app, ["aws", "--help"])
    assert result.exit_code == 0
    assert "AWS" in result.output or "aws" in result.output.lower()


def test_list_instances_empty() -> None:
    with patch("devops_framework.cli.aws.EC2Client") as MockEC2:
        MockEC2.return_value.list_instances.return_value = []
        result = runner.invoke(app, ["aws", "list-instances"])
    assert result.exit_code == 0


def test_list_instances_with_data() -> None:
    fake_instance = {
        "InstanceId": "i-12345",
        "State": {"Name": "running"},
        "InstanceType": "t3.micro",
        "PrivateIpAddress": "10.0.0.1",
        "Tags": [{"Key": "Name", "Value": "web-server"}],
    }
    with patch("devops_framework.cli.aws.EC2Client") as MockEC2:
        MockEC2.return_value.list_instances.return_value = [fake_instance]
        result = runner.invoke(app, ["aws", "list-instances"])
    assert result.exit_code == 0
    assert "i-12345" in result.output


def test_list_functions_empty() -> None:
    with patch("devops_framework.cli.aws.LambdaClient") as MockLambda:
        MockLambda.return_value.list_functions.return_value = []
        result = runner.invoke(app, ["aws", "list-functions"])
    assert result.exit_code == 0


def test_list_db_instances_empty() -> None:
    with patch("devops_framework.cli.aws.RDSClient") as MockRDS:
        MockRDS.return_value.list_instances.return_value = []
        result = runner.invoke(app, ["aws", "list-db-instances"])
    assert result.exit_code == 0


def test_list_log_groups_empty() -> None:
    with patch("devops_framework.cli.aws.CloudWatchClient") as MockCW:
        MockCW.return_value.list_log_groups.return_value = []
        result = runner.invoke(app, ["aws", "list-log-groups"])
    assert result.exit_code == 0

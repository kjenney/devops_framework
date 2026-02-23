"""Tests for aws/cloudwatch.py using moto."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import boto3
import pytest
from moto import mock_aws

from devops_framework.aws.cloudwatch import CloudWatchClient
from devops_framework.core.exceptions import ResourceNotFoundError


@pytest.fixture()
def cw_client():
    with mock_aws():
        yield CloudWatchClient(region="us-east-1")


@pytest.fixture()
def log_group(cw_client: CloudWatchClient) -> str:
    boto3.client("logs", region_name="us-east-1").create_log_group(logGroupName="/test/group")
    return "/test/group"


def test_list_metrics_empty(cw_client: CloudWatchClient) -> None:
    metrics = cw_client.list_metrics()
    assert isinstance(metrics, list)


def test_list_log_groups_empty(cw_client: CloudWatchClient) -> None:
    assert cw_client.list_log_groups() == []


def test_list_log_groups_finds_created(cw_client: CloudWatchClient, log_group: str) -> None:
    groups = cw_client.list_log_groups()
    names = [g["logGroupName"] for g in groups]
    assert log_group in names


def test_list_log_groups_prefix_filter(cw_client: CloudWatchClient, log_group: str) -> None:
    groups = cw_client.list_log_groups(prefix="/test")
    assert len(groups) >= 1


def test_get_metric_statistics(cw_client: CloudWatchClient) -> None:
    now = datetime.now(timezone.utc)
    datapoints = cw_client.get_metric_statistics(
        namespace="AWS/EC2",
        metric_name="CPUUtilization",
        dimensions=[{"Name": "InstanceId", "Value": "i-12345"}],
        start_time=now - timedelta(hours=1),
        end_time=now,
    )
    assert isinstance(datapoints, list)


def test_filter_log_events_not_found(cw_client: CloudWatchClient) -> None:
    with pytest.raises(ResourceNotFoundError):
        cw_client.filter_log_events("/nonexistent/group")

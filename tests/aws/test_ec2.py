"""Tests for aws/ec2.py using moto."""

from __future__ import annotations

import boto3
import pytest
from moto import mock_aws

from devops_framework.aws.ec2 import EC2Client
from devops_framework.core.exceptions import ResourceNotFoundError


@pytest.fixture()
def ec2_client():
    with mock_aws():
        yield EC2Client(region="us-east-1")


@pytest.fixture()
def instance_id(ec2_client: EC2Client) -> str:
    """Create a single moto EC2 instance and return its ID."""
    boto_ec2 = boto3.resource("ec2", region_name="us-east-1")
    [inst] = boto_ec2.create_instances(
        ImageId="ami-00000000",
        MinCount=1,
        MaxCount=1,
        InstanceType="t3.micro",
        TagSpecifications=[
            {"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": "test-inst"}]}
        ],
    )
    return inst.id


def test_list_instances_returns_list(ec2_client: EC2Client) -> None:
    instances = ec2_client.list_instances()
    assert isinstance(instances, list)


def test_list_instances_finds_created(ec2_client: EC2Client, instance_id: str) -> None:
    instances = ec2_client.list_instances()
    ids = [i["InstanceId"] for i in instances]
    assert instance_id in ids


def test_get_instance_returns_dict(ec2_client: EC2Client, instance_id: str) -> None:
    inst = ec2_client.get_instance(instance_id)
    assert inst["InstanceId"] == instance_id


def test_get_instance_not_found(ec2_client: EC2Client) -> None:
    with pytest.raises(ResourceNotFoundError):
        ec2_client.get_instance("i-nonexistent00000000")


def test_list_running_instances(ec2_client: EC2Client, instance_id: str) -> None:
    running = ec2_client.list_running_instances()
    assert any(i["InstanceId"] == instance_id for i in running)


def test_stop_and_start_instance(ec2_client: EC2Client, instance_id: str) -> None:
    stopped = ec2_client.stop_instance(instance_id)
    assert stopped["InstanceId"] == instance_id

    started = ec2_client.start_instance(instance_id)
    assert started["InstanceId"] == instance_id


def test_get_instance_status(ec2_client: EC2Client, instance_id: str) -> None:
    status = ec2_client.get_instance_status(instance_id)
    assert "InstanceId" in status

"""Tests for aws/rds.py using moto."""

from __future__ import annotations

import boto3
import pytest
from moto import mock_aws

from devops_framework.aws.rds import RDSClient
from devops_framework.core.exceptions import ResourceNotFoundError


@pytest.fixture()
def rds_client():
    with mock_aws():
        yield RDSClient(region="us-east-1")


@pytest.fixture()
def db_identifier(rds_client: RDSClient) -> str:
    boto_rds = boto3.client("rds", region_name="us-east-1")
    boto_rds.create_db_instance(
        DBInstanceIdentifier="test-db",
        DBInstanceClass="db.t3.micro",
        Engine="mysql",
        MasterUsername="admin",
        MasterUserPassword="password123",
        AllocatedStorage=20,
    )
    return "test-db"


def test_list_instances_empty(rds_client: RDSClient) -> None:
    assert rds_client.list_instances() == []


def test_list_instances_finds_created(rds_client: RDSClient, db_identifier: str) -> None:
    instances = rds_client.list_instances()
    ids = [i["DBInstanceIdentifier"] for i in instances]
    assert db_identifier in ids


def test_get_instance(rds_client: RDSClient, db_identifier: str) -> None:
    inst = rds_client.get_instance(db_identifier)
    assert inst["DBInstanceIdentifier"] == db_identifier


def test_get_instance_not_found(rds_client: RDSClient) -> None:
    with pytest.raises(ResourceNotFoundError):
        rds_client.get_instance("nonexistent-db")

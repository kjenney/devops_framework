"""Tests for eks/clusters.py using moto."""

from __future__ import annotations

import boto3
import pytest
from moto import mock_aws

from devops_framework.eks.clusters import ClusterClient
from devops_framework.core.exceptions import ResourceNotFoundError


@pytest.fixture()
def cluster_client():
    with mock_aws():
        yield ClusterClient(region="us-east-1")


@pytest.fixture()
def cluster_name(cluster_client: ClusterClient) -> str:
    """Create a single moto EKS cluster and return its name."""
    boto_eks = boto3.client("eks", region_name="us-east-1")
    resp = boto_eks.create_cluster(
        name="test-cluster",
        version="1.28",
        roleArn="arn:aws:iam::123456789012:role/eks-service-role",
        resourcesVpcConfig={
            "subnetIds": ["subnet-12345", "subnet-67890"],
        },
    )
    return resp["cluster"]["name"]


def test_list_clusters_returns_list(cluster_client: ClusterClient) -> None:
    clusters = cluster_client.list_clusters()
    assert isinstance(clusters, list)


def test_list_clusters_finds_created(cluster_client: ClusterClient, cluster_name: str) -> None:
    clusters = cluster_client.list_clusters()
    cluster_names = [c["name"] for c in clusters]
    assert cluster_name in cluster_names


def test_list_clusters_empty(cluster_client: ClusterClient) -> None:
    clusters = cluster_client.list_clusters()
    assert clusters == []


def test_get_cluster_returns_dict(cluster_client: ClusterClient, cluster_name: str) -> None:
    cluster = cluster_client.get_cluster(cluster_name)
    assert cluster["name"] == cluster_name


def test_get_cluster_not_found(cluster_client: ClusterClient) -> None:
    with pytest.raises(ResourceNotFoundError):
        cluster_client.get_cluster("nonexistent-cluster")


def test_list_clusters_multiple(cluster_client: ClusterClient) -> None:
    """Test listing multiple clusters."""
    boto_eks = boto3.client("eks", region_name="us-east-1")
    for i in range(1, 4):
        boto_eks.create_cluster(
            name=f"cluster-{i}",
            version="1.28",
            roleArn="arn:aws:iam::123456789012:role/eks-service-role",
            resourcesVpcConfig={
                "subnetIds": ["subnet-12345", "subnet-67890"],
            },
        )

    clusters = cluster_client.list_clusters()
    cluster_names = [c["name"] for c in clusters]
    assert len(clusters) == 3
    assert "cluster-1" in cluster_names
    assert "cluster-2" in cluster_names
    assert "cluster-3" in cluster_names


def test_cluster_contains_metadata(cluster_client: ClusterClient, cluster_name: str) -> None:
    """Test that cluster metadata is returned."""
    cluster = cluster_client.get_cluster(cluster_name)
    assert "name" in cluster
    assert "status" in cluster
    assert "version" in cluster
    assert "roleArn" in cluster
    assert "resourcesVpcConfig" in cluster

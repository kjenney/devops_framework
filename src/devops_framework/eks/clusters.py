"""EKS cluster management client using AWS API."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from botocore.exceptions import ClientError

from devops_framework.aws.base import AWSBaseClient
from devops_framework.core.exceptions import ResourceNotFoundError


class ClusterClient(AWSBaseClient):
    """Client for AWS EKS cluster operations."""

    @cached_property
    def _eks(self) -> Any:
        return self._boto_client("eks")

    def list_clusters(self) -> list[dict[str, Any]]:
        """
        List all EKS clusters in the AWS account.

        Returns a list of cluster dicts with cluster name, ARN, status, version, and other metadata.
        """
        clusters: list[dict[str, Any]] = []
        try:
            # First, list cluster names using paginator
            paginator = self._eks.get_paginator("list_clusters")
            cluster_names: list[str] = []
            for page in paginator.paginate():
                cluster_names.extend(page.get("clusters", []))

            # Then, describe the clusters to get full details
            if cluster_names:
                # Describe clusters in batches (AWS limits to 100 per call)
                for i in range(0, len(cluster_names), 100):
                    batch = cluster_names[i : i + 100]
                    resp = self._eks.describe_clusters(names=batch)
                    clusters.extend(resp.get("clusters", []))
        except ClientError as exc:
            raise self._wrap_client_error(exc, "EKS list_clusters failed") from exc
        return clusters

    def get_cluster(self, cluster_name: str) -> dict[str, Any]:
        """Return a single cluster dict or raise ResourceNotFoundError."""
        try:
            resp = self._eks.describe_cluster(name=cluster_name)
            cluster = resp.get("cluster")
            if not cluster:
                raise ResourceNotFoundError("EKS Cluster", cluster_name)
            return cluster
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code == "ResourceNotFoundException":
                raise ResourceNotFoundError("EKS Cluster", cluster_name) from exc
            raise self._wrap_client_error(exc, f"EKS describe_cluster({cluster_name})") from exc

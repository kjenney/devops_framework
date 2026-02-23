"""RDS client for listing and describing database instances and clusters."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from botocore.exceptions import ClientError

from devops_framework.aws.base import AWSBaseClient
from devops_framework.core.exceptions import ResourceNotFoundError


class RDSClient(AWSBaseClient):
    """Client for RDS operations."""

    @cached_property
    def _rds(self) -> Any:
        return self._boto_client("rds")

    def list_instances(self, db_instance_identifier: str | None = None) -> list[dict[str, Any]]:
        """List RDS DB instances, optionally filtered by identifier."""
        kwargs: dict[str, Any] = {}
        if db_instance_identifier:
            kwargs["DBInstanceIdentifier"] = db_instance_identifier
        instances: list[dict[str, Any]] = []
        try:
            paginator = self._rds.get_paginator("describe_db_instances")
            for page in paginator.paginate(**kwargs):
                instances.extend(page.get("DBInstances", []))
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code == "DBInstanceNotFound":
                return []
            raise self._wrap_client_error(exc, "RDS describe_db_instances failed") from exc
        return instances

    def get_instance(self, db_instance_identifier: str) -> dict[str, Any]:
        """Return a single DB instance dict or raise ResourceNotFoundError."""
        results = self.list_instances(db_instance_identifier=db_instance_identifier)
        if not results:
            raise ResourceNotFoundError("RDS DBInstance", db_instance_identifier)
        return results[0]

    def list_clusters(self, db_cluster_identifier: str | None = None) -> list[dict[str, Any]]:
        """List RDS DB clusters (Aurora), optionally filtered by identifier."""
        kwargs: dict[str, Any] = {}
        if db_cluster_identifier:
            kwargs["DBClusterIdentifier"] = db_cluster_identifier
        clusters: list[dict[str, Any]] = []
        try:
            paginator = self._rds.get_paginator("describe_db_clusters")
            for page in paginator.paginate(**kwargs):
                clusters.extend(page.get("DBClusters", []))
        except ClientError as exc:
            raise self._wrap_client_error(exc, "RDS describe_db_clusters failed") from exc
        return clusters

    def get_cluster(self, db_cluster_identifier: str) -> dict[str, Any]:
        """Return a single DB cluster dict or raise ResourceNotFoundError."""
        results = self.list_clusters(db_cluster_identifier=db_cluster_identifier)
        if not results:
            raise ResourceNotFoundError("RDS DBCluster", db_cluster_identifier)
        return results[0]

    def get_instance_events(
        self,
        db_instance_identifier: str,
        duration: int = 1440,
    ) -> list[dict[str, Any]]:
        """Return recent events for a DB instance (duration in minutes, default 24h)."""
        try:
            resp = self._rds.describe_events(
                SourceIdentifier=db_instance_identifier,
                SourceType="db-instance",
                Duration=duration,
            )
        except ClientError as exc:
            raise self._wrap_client_error(exc, f"RDS describe_events({db_instance_identifier})") from exc
        return resp.get("Events", [])

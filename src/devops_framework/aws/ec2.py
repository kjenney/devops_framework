"""EC2 client for listing and describing instances."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from botocore.exceptions import ClientError

from devops_framework.aws.base import AWSBaseClient
from devops_framework.core.exceptions import AWSAPIError, ResourceNotFoundError


class EC2Client(AWSBaseClient):
    """Client for EC2 operations."""

    @cached_property
    def _ec2(self) -> Any:
        return self._boto_client("ec2")

    def list_instances(
        self,
        filters: list[dict[str, Any]] | None = None,
        instance_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        List EC2 instances with optional filters.

        Returns a flat list of instance dicts (not reservation wrappers).
        """
        kwargs: dict[str, Any] = {}
        if filters:
            kwargs["Filters"] = filters
        if instance_ids:
            kwargs["InstanceIds"] = instance_ids

        instances: list[dict[str, Any]] = []
        try:
            paginator = self._ec2.get_paginator("describe_instances")
            for page in paginator.paginate(**kwargs):
                for reservation in page.get("Reservations", []):
                    instances.extend(reservation.get("Instances", []))
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code == "InvalidInstanceID.NotFound":
                return []
            raise self._wrap_client_error(exc, "EC2 describe_instances failed") from exc
        return instances

    def get_instance(self, instance_id: str) -> dict[str, Any]:
        """Return a single instance dict or raise ResourceNotFoundError."""
        results = self.list_instances(instance_ids=[instance_id])
        if not results:
            raise ResourceNotFoundError("EC2 Instance", instance_id)
        return results[0]

    def list_running_instances(self) -> list[dict[str, Any]]:
        """Return all instances in the 'running' state."""
        return self.list_instances(filters=[{"Name": "instance-state-name", "Values": ["running"]}])

    def get_instance_status(self, instance_id: str) -> dict[str, Any]:
        """Return instance and system status checks for a single instance."""
        try:
            resp = self._ec2.describe_instance_status(
                InstanceIds=[instance_id],
                IncludeAllInstances=True,
            )
        except ClientError as exc:
            raise self._wrap_client_error(exc, f"describe_instance_status({instance_id})") from exc
        statuses = resp.get("InstanceStatuses", [])
        if not statuses:
            raise ResourceNotFoundError("EC2 Instance", instance_id)
        return statuses[0]

    def stop_instance(self, instance_id: str) -> dict[str, Any]:
        """Stop an EC2 instance. Returns the StoppingInstances response."""
        try:
            resp = self._ec2.stop_instances(InstanceIds=[instance_id])
        except ClientError as exc:
            raise self._wrap_client_error(exc, f"stop_instances({instance_id})") from exc
        stopping = resp.get("StoppingInstances", [])
        if not stopping:
            raise AWSAPIError(f"stop_instances returned empty response for {instance_id}")
        return stopping[0]

    def start_instance(self, instance_id: str) -> dict[str, Any]:
        """Start an EC2 instance. Returns the StartingInstances response."""
        try:
            resp = self._ec2.start_instances(InstanceIds=[instance_id])
        except ClientError as exc:
            raise self._wrap_client_error(exc, f"start_instances({instance_id})") from exc
        starting = resp.get("StartingInstances", [])
        if not starting:
            raise AWSAPIError(f"start_instances returned empty response for {instance_id}")
        return starting[0]

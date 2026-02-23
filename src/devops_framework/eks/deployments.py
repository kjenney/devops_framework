"""Kubernetes Deployment client."""

from __future__ import annotations

from typing import Any

from kubernetes.client.exceptions import ApiException
from kubernetes.client.models import V1Deployment

from devops_framework.core.exceptions import ResourceNotFoundError
from devops_framework.eks.base import EKSBaseClient


class DeploymentClient(EKSBaseClient):
    """Client for Kubernetes Deployment operations."""

    def list_deployments(
        self,
        namespace: str | None = None,
        label_selector: str | None = None,
    ) -> list[V1Deployment]:
        """List deployments in the given namespace."""
        ns = namespace or self._namespace
        kwargs: dict[str, Any] = {}
        if label_selector:
            kwargs["label_selector"] = label_selector
        try:
            resp = self.apps_v1.list_namespaced_deployment(namespace=ns, **kwargs)
        except ApiException as exc:
            raise self._wrap_api_exception(exc, f"list_namespaced_deployment(ns={ns})") from exc
        return resp.items

    def get_deployment(self, deployment_name: str, namespace: str | None = None) -> V1Deployment:
        """Return a single Deployment or raise ResourceNotFoundError."""
        ns = namespace or self._namespace
        try:
            return self.apps_v1.read_namespaced_deployment(name=deployment_name, namespace=ns)
        except ApiException as exc:
            if exc.status == 404:
                raise ResourceNotFoundError("Deployment", deployment_name) from exc
            raise self._wrap_api_exception(exc, f"read_namespaced_deployment({deployment_name})") from exc

    def scale_deployment(
        self,
        deployment_name: str,
        replicas: int,
        namespace: str | None = None,
    ) -> V1Deployment:
        """Scale a deployment to the specified number of replicas."""
        ns = namespace or self._namespace
        try:
            body = {"spec": {"replicas": replicas}}
            return self.apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=ns,
                body=body,
            )
        except ApiException as exc:
            if exc.status == 404:
                raise ResourceNotFoundError("Deployment", deployment_name) from exc
            raise self._wrap_api_exception(
                exc, f"patch_namespaced_deployment_scale({deployment_name}, replicas={replicas})"
            ) from exc

    def restart_deployment(self, deployment_name: str, namespace: str | None = None) -> V1Deployment:
        """Trigger a rolling restart by patching the pod template annotation."""
        from datetime import datetime, timezone

        ns = namespace or self._namespace
        try:
            body = {
                "spec": {
                    "template": {
                        "metadata": {
                            "annotations": {
                                "kubectl.kubernetes.io/restartedAt": datetime.now(timezone.utc).isoformat()
                            }
                        }
                    }
                }
            }
            return self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=ns,
                body=body,
            )
        except ApiException as exc:
            if exc.status == 404:
                raise ResourceNotFoundError("Deployment", deployment_name) from exc
            raise self._wrap_api_exception(exc, f"restart_deployment({deployment_name})") from exc

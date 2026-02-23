"""Kubernetes Pod client."""

from __future__ import annotations

from typing import Any

from kubernetes.client.exceptions import ApiException
from kubernetes.client.models import V1Pod

from devops_framework.core.exceptions import ResourceNotFoundError
from devops_framework.eks.base import EKSBaseClient


class PodClient(EKSBaseClient):
    """Client for Kubernetes Pod operations."""

    def list_pods(self, namespace: str | None = None, label_selector: str | None = None) -> list[V1Pod]:
        """List pods in the given namespace (defaults to client namespace)."""
        ns = namespace or self._namespace
        kwargs: dict[str, Any] = {}
        if label_selector:
            kwargs["label_selector"] = label_selector
        try:
            resp = self.core_v1.list_namespaced_pod(namespace=ns, **kwargs)
        except ApiException as exc:
            raise self._wrap_api_exception(exc, f"list_namespaced_pod(ns={ns})") from exc
        return resp.items

    def get_pod(self, pod_name: str, namespace: str | None = None) -> V1Pod:
        """Return a single Pod or raise ResourceNotFoundError."""
        ns = namespace or self._namespace
        try:
            return self.core_v1.read_namespaced_pod(name=pod_name, namespace=ns)
        except ApiException as exc:
            if exc.status == 404:
                raise ResourceNotFoundError("Pod", pod_name) from exc
            raise self._wrap_api_exception(exc, f"read_namespaced_pod({pod_name}, ns={ns})") from exc

    def get_pod_logs(
        self,
        pod_name: str,
        namespace: str | None = None,
        container: str | None = None,
        tail_lines: int = 100,
        previous: bool = False,
    ) -> str:
        """Return log output from a pod container."""
        ns = namespace or self._namespace
        kwargs: dict[str, Any] = {
            "name": pod_name,
            "namespace": ns,
            "tail_lines": tail_lines,
            "previous": previous,
        }
        if container:
            kwargs["container"] = container
        try:
            return self.core_v1.read_namespaced_pod_log(**kwargs)
        except ApiException as exc:
            if exc.status == 404:
                raise ResourceNotFoundError("Pod", pod_name) from exc
            raise self._wrap_api_exception(exc, f"read_namespaced_pod_log({pod_name})") from exc

    def delete_pod(self, pod_name: str, namespace: str | None = None) -> None:
        """Delete a pod (triggers restart if managed by a controller)."""
        ns = namespace or self._namespace
        try:
            self.core_v1.delete_namespaced_pod(name=pod_name, namespace=ns)
        except ApiException as exc:
            if exc.status == 404:
                raise ResourceNotFoundError("Pod", pod_name) from exc
            raise self._wrap_api_exception(exc, f"delete_namespaced_pod({pod_name})") from exc

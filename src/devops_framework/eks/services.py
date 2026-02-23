"""Kubernetes Service client."""

from __future__ import annotations

from typing import Any

from kubernetes.client.exceptions import ApiException
from kubernetes.client.models import V1Service

from devops_framework.core.exceptions import ResourceNotFoundError
from devops_framework.eks.base import EKSBaseClient


class ServiceClient(EKSBaseClient):
    """Client for Kubernetes Service operations."""

    def list_services(
        self,
        namespace: str | None = None,
        label_selector: str | None = None,
    ) -> list[V1Service]:
        """List services in the given namespace."""
        ns = namespace or self._namespace
        kwargs: dict[str, Any] = {}
        if label_selector:
            kwargs["label_selector"] = label_selector
        try:
            resp = self.core_v1.list_namespaced_service(namespace=ns, **kwargs)
        except ApiException as exc:
            raise self._wrap_api_exception(exc, f"list_namespaced_service(ns={ns})") from exc
        return resp.items

    def get_service(self, service_name: str, namespace: str | None = None) -> V1Service:
        """Return a single Service or raise ResourceNotFoundError."""
        ns = namespace or self._namespace
        try:
            return self.core_v1.read_namespaced_service(name=service_name, namespace=ns)
        except ApiException as exc:
            if exc.status == 404:
                raise ResourceNotFoundError("Service", service_name) from exc
            raise self._wrap_api_exception(exc, f"read_namespaced_service({service_name})") from exc

    def get_endpoints(self, service_name: str, namespace: str | None = None) -> Any:
        """Return the Endpoints object for a Service."""
        ns = namespace or self._namespace
        try:
            return self.core_v1.read_namespaced_endpoints(name=service_name, namespace=ns)
        except ApiException as exc:
            if exc.status == 404:
                raise ResourceNotFoundError("Endpoints", service_name) from exc
            raise self._wrap_api_exception(exc, f"read_namespaced_endpoints({service_name})") from exc

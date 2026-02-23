"""EKS base client: kubeconfig loading, CoreV1/AppsV1 API access."""

from __future__ import annotations

from functools import cached_property
from typing import Any

import kubernetes
import kubernetes.client
import kubernetes.config
from kubernetes.client.exceptions import ApiException

from devops_framework.core.base import IntegrationBaseClient
from devops_framework.core.config import Config
from devops_framework.core.exceptions import EKSAuthError, KubernetesAPIError


class EKSBaseClient(IntegrationBaseClient):
    """
    Base class for all EKS/Kubernetes clients.

    Loads kubeconfig lazily. Supports in-cluster config (when running inside a pod)
    with fallback to local kubeconfig file.
    """

    def __init__(
        self,
        namespace: str | None = None,
        context: str | None = None,
        config: Config | None = None,
    ) -> None:
        super().__init__(config)
        self._namespace = namespace or self.config.eks_namespace
        self._context = context or self.config.eks_context
        self._kubeconfig = self.config.eks_kubeconfig
        self._k8s_config_loaded = False

    @property
    def namespace(self) -> str:
        return self._namespace

    def _ensure_config(self) -> None:
        if self._k8s_config_loaded:
            return
        try:
            kubernetes.config.load_kube_config(
                config_file=self._kubeconfig,
                context=self._context,
            )
        except kubernetes.config.config_exception.ConfigException:
            try:
                kubernetes.config.load_incluster_config()
            except kubernetes.config.config_exception.ConfigException as exc:
                raise EKSAuthError(
                    "Failed to load Kubernetes configuration: no kubeconfig found and not running in-cluster"
                ) from exc
        self._k8s_config_loaded = True

    @cached_property
    def core_v1(self) -> kubernetes.client.CoreV1Api:
        self._ensure_config()
        return kubernetes.client.CoreV1Api()

    @cached_property
    def apps_v1(self) -> kubernetes.client.AppsV1Api:
        self._ensure_config()
        return kubernetes.client.AppsV1Api()

    def health_check(self) -> bool:
        """Verify Kubernetes connectivity by listing namespaces."""
        try:
            self.core_v1.list_namespace(limit=1)
            return True
        except (EKSAuthError, ApiException):
            return False

    @staticmethod
    def _wrap_api_exception(exc: ApiException, context: str) -> KubernetesAPIError:
        return KubernetesAPIError(
            f"{context}: [{exc.status}] {exc.reason}",
            status_code=exc.status,
            details={"reason": exc.reason, "body": exc.body},
        )

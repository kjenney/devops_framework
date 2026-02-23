"""Datadog base client: env var + YAML config auth."""

from __future__ import annotations

from functools import cached_property

from datadog_api_client import ApiClient, Configuration

from devops_framework.core.base import IntegrationBaseClient
from devops_framework.core.config import Config
from devops_framework.core.exceptions import DatadogAuthError


class DatadogBaseClient(IntegrationBaseClient):
    """
    Base class for all Datadog API clients.

    Auth priority: DD_API_KEY / DD_APP_KEY env vars → YAML config.
    """

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)
        self._validate_auth()

    def _validate_auth(self) -> None:
        if not self.config.datadog_api_key:
            raise DatadogAuthError(
                "Datadog API key is not set. "
                "Set DD_API_KEY environment variable or datadog.api_key in your config.yaml."
            )
        if not self.config.datadog_app_key:
            raise DatadogAuthError(
                "Datadog Application key is not set. "
                "Set DD_APP_KEY environment variable or datadog.app_key in your config.yaml."
            )

    @cached_property
    def _dd_configuration(self) -> Configuration:
        cfg = Configuration()
        cfg.api_key["apiKeyAuth"] = self.config.datadog_api_key
        cfg.api_key["appKeyAuth"] = self.config.datadog_app_key
        cfg.server_variables["site"] = self.config.datadog_site
        return cfg

    @cached_property
    def api_client(self) -> ApiClient:
        return ApiClient(self._dd_configuration)

    def health_check(self) -> bool:
        """Verify Datadog connectivity by validating the API key."""
        try:
            from datadog_api_client.v1.api.authentication_api import AuthenticationApi

            with ApiClient(self._dd_configuration) as client:
                api = AuthenticationApi(client)
                resp = api.validate()
                return bool(resp.valid)
        except Exception:
            return False

"""AWS base client: session management, retry config, region handling."""

from __future__ import annotations

from functools import cached_property
from typing import Any

import boto3
import botocore.config
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from devops_framework.core.base import IntegrationBaseClient
from devops_framework.core.config import Config
from devops_framework.core.exceptions import AWSAPIError, AWSAuthError


_RETRY_CONFIG = botocore.config.Config(
    retries={"max_attempts": 3, "mode": "adaptive"},
)


class AWSBaseClient(IntegrationBaseClient):
    """
    Base class for all AWS service clients.

    Lazily initialises a boto3 session and individual service clients.
    Authentication follows standard boto3 credential resolution:
      env vars → ~/.aws/credentials → IAM instance role → etc.
    """

    def __init__(
        self, region: str | None = None, profile: str | None = None, config: Config | None = None
    ) -> None:
        super().__init__(config)
        self._region = region or self.config.aws_region
        self._profile = profile or self.config.aws_profile

    @property
    def region(self) -> str:
        return self._region

    @cached_property
    def session(self) -> boto3.Session:
        kwargs: dict[str, Any] = {"region_name": self._region}
        if self._profile:
            kwargs["profile_name"] = self._profile
        try:
            return boto3.Session(**kwargs)
        except (BotoCoreError, Exception) as exc:
            raise AWSAuthError(f"Failed to create AWS session: {exc}") from exc

    def _boto_client(self, service: str) -> Any:
        """Return a boto3 service client with retry config."""
        try:
            return self.session.client(service, config=_RETRY_CONFIG)
        except NoCredentialsError as exc:
            raise AWSAuthError("AWS credentials not found") from exc
        except (BotoCoreError, ClientError) as exc:
            raise AWSAPIError(f"Failed to create {service} client: {exc}") from exc

    def health_check(self) -> bool:
        """Verify AWS credentials are valid by calling STS GetCallerIdentity."""
        try:
            sts = self._boto_client("sts")
            sts.get_caller_identity()
            return True
        except (AWSAuthError, AWSAPIError):
            return False

    @staticmethod
    def _wrap_client_error(exc: ClientError, context: str) -> AWSAPIError:
        code = exc.response.get("Error", {}).get("Code", "Unknown")
        message = exc.response.get("Error", {}).get("Message", str(exc))
        status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        return AWSAPIError(
            f"{context}: [{code}] {message}",
            status_code=status,
            details={"error_code": code},
        )

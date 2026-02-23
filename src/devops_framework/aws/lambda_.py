"""Lambda client for listing functions and inspecting invocations."""

from __future__ import annotations

import base64
import json
from functools import cached_property
from typing import Any

from botocore.exceptions import ClientError

from devops_framework.aws.base import AWSBaseClient
from devops_framework.core.exceptions import AWSAPIError, ResourceNotFoundError


class LambdaClient(AWSBaseClient):
    """Client for AWS Lambda operations."""

    @cached_property
    def _lambda(self) -> Any:
        return self._boto_client("lambda")

    def list_functions(self) -> list[dict[str, Any]]:
        """Return all Lambda functions in the configured region."""
        functions: list[dict[str, Any]] = []
        try:
            paginator = self._lambda.get_paginator("list_functions")
            for page in paginator.paginate():
                functions.extend(page.get("Functions", []))
        except ClientError as exc:
            raise self._wrap_client_error(exc, "Lambda list_functions failed") from exc
        return functions

    def get_function(self, function_name: str) -> dict[str, Any]:
        """Return the configuration + code location for a Lambda function."""
        try:
            return self._lambda.get_function(FunctionName=function_name)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code == "ResourceNotFoundException":
                raise ResourceNotFoundError("Lambda Function", function_name) from exc
            raise self._wrap_client_error(exc, f"Lambda get_function({function_name})") from exc

    def invoke(
        self,
        function_name: str,
        payload: dict[str, Any] | None = None,
        invocation_type: str = "RequestResponse",
    ) -> dict[str, Any]:
        """
        Invoke a Lambda function and return the parsed response.

        ``invocation_type`` is one of ``RequestResponse`` (sync) or ``Event`` (async).
        """
        kwargs: dict[str, Any] = {
            "FunctionName": function_name,
            "InvocationType": invocation_type,
        }
        if payload is not None:
            kwargs["Payload"] = json.dumps(payload).encode()

        try:
            resp = self._lambda.invoke(**kwargs)
        except ClientError as exc:
            raise self._wrap_client_error(exc, f"Lambda invoke({function_name})") from exc

        result: dict[str, Any] = {
            "StatusCode": resp.get("StatusCode"),
            "FunctionError": resp.get("FunctionError"),
            "LogResult": None,
            "Payload": None,
        }

        if "LogResult" in resp:
            result["LogResult"] = base64.b64decode(resp["LogResult"]).decode("utf-8", errors="replace")

        if "Payload" in resp:
            raw = resp["Payload"].read()
            try:
                result["Payload"] = json.loads(raw)
            except json.JSONDecodeError:
                result["Payload"] = raw.decode("utf-8", errors="replace")

        if resp.get("FunctionError"):
            raise AWSAPIError(
                f"Lambda function {function_name!r} returned error: {result['Payload']}",
                status_code=resp.get("StatusCode"),
                details={"payload": result["Payload"]},
            )

        return result

    def get_function_configuration(self, function_name: str) -> dict[str, Any]:
        """Return only the configuration (not code) for a Lambda function."""
        try:
            return self._lambda.get_function_configuration(FunctionName=function_name)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code == "ResourceNotFoundException":
                raise ResourceNotFoundError("Lambda Function", function_name) from exc
            raise self._wrap_client_error(exc, f"Lambda get_function_configuration({function_name})") from exc

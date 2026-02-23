"""Tests for aws/lambda_.py using moto."""

from __future__ import annotations

import json
import zipfile
from io import BytesIO

import boto3
import pytest
from moto import mock_aws

from devops_framework.aws.lambda_ import LambdaClient
from devops_framework.core.exceptions import ResourceNotFoundError


def _make_lambda_zip(handler_code: str = "def handler(event, context): return {'ok': True}") -> bytes:
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("lambda_function.py", handler_code)
    return buf.getvalue()


@pytest.fixture()
def lambda_client():
    with mock_aws():
        yield LambdaClient(region="us-east-1")


@pytest.fixture()
def function_name(lambda_client: LambdaClient) -> str:
    iam = boto3.client("iam", region_name="us-east-1")
    role = iam.create_role(
        RoleName="lambda-role",
        AssumeRolePolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}],
            }
        ),
    )
    role_arn = role["Role"]["Arn"]

    boto3.client("lambda", region_name="us-east-1").create_function(
        FunctionName="test-function",
        Runtime="python3.12",
        Role=role_arn,
        Handler="lambda_function.handler",
        Code={"ZipFile": _make_lambda_zip()},
    )
    return "test-function"


def test_list_functions_empty(lambda_client: LambdaClient) -> None:
    assert lambda_client.list_functions() == []


def test_list_functions_finds_created(lambda_client: LambdaClient, function_name: str) -> None:
    fns = lambda_client.list_functions()
    names = [f["FunctionName"] for f in fns]
    assert function_name in names


def test_get_function(lambda_client: LambdaClient, function_name: str) -> None:
    fn = lambda_client.get_function(function_name)
    assert fn["Configuration"]["FunctionName"] == function_name


def test_get_function_not_found(lambda_client: LambdaClient) -> None:
    with pytest.raises(ResourceNotFoundError):
        lambda_client.get_function("nonexistent-function")


def test_invoke_function(lambda_client: LambdaClient, function_name: str) -> None:
    """Invoke is tested with a patched boto3 client to avoid docker dependency."""
    from io import BytesIO
    from unittest.mock import MagicMock, patch

    fake_payload = BytesIO(b'{"ok": true}')
    fake_response = {
        "StatusCode": 200,
        "Payload": fake_payload,
    }

    with patch.object(lambda_client, "_lambda", create=True) as mock_lambda_client:
        mock_lambda_client.invoke.return_value = fake_response
        result = lambda_client.invoke(function_name, payload={"key": "value"})

    assert result["StatusCode"] == 200
    assert result["Payload"] == {"ok": True}

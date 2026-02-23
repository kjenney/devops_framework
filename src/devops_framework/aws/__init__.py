"""AWS integration: EC2, RDS, Lambda, CloudWatch."""

from devops_framework.aws.cloudwatch import CloudWatchClient
from devops_framework.aws.ec2 import EC2Client
from devops_framework.aws.lambda_ import LambdaClient
from devops_framework.aws.rds import RDSClient

__all__ = ["EC2Client", "RDSClient", "LambdaClient", "CloudWatchClient"]

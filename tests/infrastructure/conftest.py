import boto3
import pytest
from botocore.config import Config
from moto import mock_aws


@pytest.fixture(autouse=True)
def aws_credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")


@pytest.fixture
def s3_client():
    with mock_aws():
        client = boto3.client(
            "s3",
            region_name="eu-west-1",
            config=Config(signature_version="s3v4"),
        )
        client.create_bucket(
            Bucket="normativa-test-files",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
        )
        yield client

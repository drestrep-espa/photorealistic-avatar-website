import boto3
import pytest
from moto import mock_aws

from src.infrastructure.ssm_runtime_settings_loader import (
    RuntimeSettings,
    SsmRuntimeSettingsLoader,
)

OPENAI_API_KEY_PARAMETER = "/normativa-precheck/openai-api-key"
VECTOR_STORE_ID_PARAMETER = "/normativa-precheck/vector-store-id"


def test_load_returns_runtime_settings_from_ssm():
    with mock_aws():
        client = boto3.client("ssm", region_name="eu-west-1")
        client.put_parameter(
            Name=OPENAI_API_KEY_PARAMETER,
            Type="SecureString",
            Value="fake-openai-api-key",
        )
        client.put_parameter(
            Name=VECTOR_STORE_ID_PARAMETER,
            Type="String",
            Value="fake-vector-store-id",
        )
        loader = SsmRuntimeSettingsLoader(
            openai_api_key_parameter=OPENAI_API_KEY_PARAMETER,
            vector_store_id_parameter=VECTOR_STORE_ID_PARAMETER,
            client=client,
        )

        settings = loader.load()

    assert settings == RuntimeSettings(
        openai_api_key="fake-openai-api-key",
        vector_store_id="fake-vector-store-id",
    )


def test_load_reuses_cached_settings_after_first_ssm_read():
    class RecordingSsmClient:
        def __init__(self):
            self.calls = 0

        def get_parameters(self, **kwargs):
            self.calls += 1
            return {
                "Parameters": [
                    {
                        "Name": OPENAI_API_KEY_PARAMETER,
                        "Value": "fake-openai-api-key",
                    },
                    {
                        "Name": VECTOR_STORE_ID_PARAMETER,
                        "Value": "fake-vector-store-id",
                    },
                ],
                "InvalidParameters": [],
            }

    client = RecordingSsmClient()
    loader = SsmRuntimeSettingsLoader(
        openai_api_key_parameter=OPENAI_API_KEY_PARAMETER,
        vector_store_id_parameter=VECTOR_STORE_ID_PARAMETER,
        client=client,
    )

    first_result = loader.load()
    second_result = loader.load()

    assert first_result is second_result
    assert client.calls == 1


def test_load_fails_when_an_ssm_parameter_is_missing():
    with mock_aws():
        client = boto3.client("ssm", region_name="eu-west-1")
        client.put_parameter(
            Name=OPENAI_API_KEY_PARAMETER,
            Type="SecureString",
            Value="fake-openai-api-key",
        )
        loader = SsmRuntimeSettingsLoader(
            openai_api_key_parameter=OPENAI_API_KEY_PARAMETER,
            vector_store_id_parameter=VECTOR_STORE_ID_PARAMETER,
            client=client,
        )

        with pytest.raises(
            RuntimeError,
            match="/normativa-precheck/vector-store-id",
        ):
            loader.load()

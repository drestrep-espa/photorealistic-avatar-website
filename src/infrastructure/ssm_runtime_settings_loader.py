import os
from dataclasses import dataclass
from typing import Any

import boto3

DEFAULT_OPENAI_API_KEY_PARAMETER = "/normativa-precheck/openai-api-key"
DEFAULT_VECTOR_STORE_ID_PARAMETER = "/normativa-precheck/vector-store-id"


@dataclass(frozen=True)
class RuntimeSettings:
    openai_api_key: str
    vector_store_id: str


class SsmRuntimeSettingsLoader:
    def __init__(
        self,
        *,
        openai_api_key_parameter: str,
        vector_store_id_parameter: str,
        client: Any | None = None,
    ) -> None:
        self._openai_api_key_parameter = openai_api_key_parameter
        self._vector_store_id_parameter = vector_store_id_parameter
        self._client = client
        self._settings: RuntimeSettings | None = None

    def load(self) -> RuntimeSettings:
        if self._settings is not None:
            return self._settings

        client = self._client or boto3.client("ssm")
        parameter_names = [
            self._openai_api_key_parameter,
            self._vector_store_id_parameter,
        ]
        response = client.get_parameters(
            Names=parameter_names,
            WithDecryption=True,
        )
        values = {
            parameter["Name"]: parameter["Value"]
            for parameter in response.get("Parameters", [])
        }
        missing_parameters = [
            parameter_name
            for parameter_name in parameter_names
            if parameter_name not in values
        ]
        if missing_parameters:
            missing = ", ".join(missing_parameters)
            raise RuntimeError(f"Faltan parámetros de configuración en SSM: {missing}")

        self._settings = RuntimeSettings(
            openai_api_key=values[self._openai_api_key_parameter],
            vector_store_id=values[self._vector_store_id_parameter],
        )
        return self._settings


runtime_settings_loader = SsmRuntimeSettingsLoader(
    openai_api_key_parameter=os.environ.get(
        "OPENAI_API_KEY_PARAMETER",
        DEFAULT_OPENAI_API_KEY_PARAMETER,
    ),
    vector_store_id_parameter=os.environ.get(
        "VECTOR_STORE_ID_PARAMETER",
        DEFAULT_VECTOR_STORE_ID_PARAMETER,
    ),
)

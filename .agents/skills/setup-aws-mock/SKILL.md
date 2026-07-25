---
name: setup-aws-mock
description: "Prepara la guía de mocks AWS para tests de infraestructura. Detecta uso de moto o localstack, verifica o instala dependencias de test cuando proceda y recomienda fixtures para adaptadores boto3 como S3, Bedrock, Textract, SQS o DynamoDB. Úsala antes de escribir o ejecutar tests de adaptadores AWS."
---

# Mock AWS

Prepara tests de infraestructura AWS para que nunca llamen a AWS real ni
requieran credenciales de producción.

## Flujo

1. Detecta la estrategia actual:
   - Busca en tests y ficheros de dependencias `moto`, `mock_aws`, `localstack`,
     `LOCALSTACK_ENDPOINT` o `endpoint_url`.
2. Si ya se usa moto, sigue el patrón local de fixtures.
3. Si ya se usa localstack, verifica la expectativa de contenedor en los
   ficheros del proyecto y no arranques Docker salvo aprobación del usuario.
4. Si no existe estrategia, prefiere moto para tests unitarios/de integración de
   adaptadores.
5. Configura credenciales AWS ficticias para tests:

```python
import os
import pytest


@pytest.fixture(autouse=True)
def aws_credentials() -> None:
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
```

6. Prefiere una fixture de pytest para setup compartido de moto:

```python
import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def aws_mock():
    with mock_aws():
        yield


@pytest.fixture
def s3_client(aws_mock):
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="test-bucket")
    return client
```

7. Para servicios con soporte parcial de moto, parchea solo la llamada al
   cliente boto3 que cruza la frontera externa.

## Guía por servicio

| Servicio | Cliente/recurso boto3 | Estrategia habitual de test |
|---|---|---|
| S3 | `boto3.client("s3")` | moto |
| SQS | `boto3.client("sqs")` | moto |
| DynamoDB | `boto3.resource("dynamodb")` | moto |
| Textract | `boto3.client("textract")` | moto o parche focalizado |
| Bedrock Runtime | `boto3.client("bedrock-runtime")` | parche focalizado cuando moto no baste |

## Resultado

Reporta la estrategia detectada, dependencia requerida, patrón de fixture
recomendado, servicios en uso y cualquier servicio que necesite un parche
focalizado en lugar de moto.

---
name: setup-aws-mock
description: Configura el entorno de mock de AWS para tests de infraestructura. Detecta si el proyecto usa moto o localstack, verifica que está instalado e indica los decoradores o fixtures necesarios para que los tests de adaptadores AWS (S3, Bedrock, Textract, DynamoDB…) no llamen a AWS real. Úsala cuando infrastructure-agent vaya a escribir o ejecutar tests de adaptadores AWS, o cuando el usuario pida "configura el mock de AWS", "prepara moto para los tests", "cómo mockeo S3 en los tests".
triggers:
  - "configura el mock de AWS"
  - "prepara moto para los tests"
  - "cómo mockeo S3"
  - "setup-aws-mock"
  - "mock de AWS para tests"
---

# Setup AWS Mock

Prepara el entorno de mock de AWS para tests de infraestructura sin llamar
a AWS real ni requerir credenciales de producción.

## 1. Detectar la estrategia en uso

```bash
grep -rn "import moto\|from moto\|mock_aws" tests/ pyproject.toml requirements*.txt
grep -rn "localstack\|localhost:4566" tests/ .env* docker-compose*.yml
```

**Si encuentra `moto`** → sigue el paso 3.
**Si no hay nada** → instala moto (paso 2).

## 2. Instalar moto (si no está)

```bash
# Detecta qué servicios boto3 usa el proyecto:
grep -rn "boto3\.client\|boto3\.resource" src/

# Instala con los servicios necesarios:
<prefijo_venv>/pip install "moto[s3,bedrock,textract,sqs,dynamodb]" --quiet
<prefijo_venv>/python -c "import moto; print('moto', moto.__version__)"
```

## 3. Fixture recomendado (moto)

```python
import os, boto3, pytest
from moto import mock_aws

@pytest.fixture(autouse=True)
def aws_credentials():
    """Credenciales ficticias — solo válidas dentro de moto, nunca llegan a AWS."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def aws_mock(aws_credentials):
    with mock_aws():
        yield

@pytest.fixture
def s3_bucket(aws_mock):
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    return "test-bucket"
```

## 4. Servicios y nivel de soporte

| Servicio | Soporte moto | Alternativa |
|---|---|---|
| S3 / SQS / DynamoDB | Completo | — |
| Textract | Parcial | `patch` sobre el cliente |
| Bedrock Runtime | Parcial | `patch` sobre `invoke_model` |

Para Bedrock con soporte parcial:

```python
from unittest.mock import patch, MagicMock

def test_bedrock_service():
    mock_body = MagicMock(read=lambda: b'{"completion": "respuesta"}')
    with patch("boto3.client") as mock_client:
        mock_client.return_value.invoke_model.return_value = {"body": mock_body}
        service = BedrockLlmService(model_id="anthropic.claude-...", region="us-east-1")
        result = service.complete("prompt de test")
    assert result == "respuesta"
```

## 5. Resultado

Entrega:
1. Estrategia en uso (moto / localstack / patch puntual).
2. Versión de moto instalada (si se instaló).
3. Servicios AWS usados en el proyecto y nivel de soporte.
4. Patrón de fixture listo para añadir a `conftest.py`.

## No Usar Cuando

Si el proyecto no usa AWS. Si ya hay fixtures de moto en `conftest.py`
correctamente configurados — no duplicar.

## Controles PSI-12

Las credenciales del fixture (`"testing"`) son ficticias exclusivas del
contexto de moto — nunca deben coincidir con credenciales reales ni
llegar a entornos de staging o producción. No configurar
`AWS_DEFAULT_REGION` con la región real de producción en los tests.
Añadir el bloque `aws_credentials` como `autouse=True` para garantizar
que ningún test escape al mock accidentalmente.

## Referencias

- Reglas de tests de infraestructura: `.claude/rules/testing.md` §Pirámide
- Agente que la invoca: `infrastructure-agent`
- Requiere: `python-sandbox` (moto debe estar en el venv)

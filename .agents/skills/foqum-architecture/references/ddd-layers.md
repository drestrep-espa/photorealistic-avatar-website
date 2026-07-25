# Capas DDD

## Tabla de capas

| Capa | Contiene | Nunca debe contener |
|---|---|---|
| `domain/` | Entidades Pydantic, value objects, puertos ABC, excepciones de negocio, constantes de dominio | FastAPI, SQLAlchemy, boto3, requests, httpx, Redis, Celery, dependencias de framework o infraestructura |
| `application/` | Casos de uso que reciben puertos de dominio y orquestan el flujo | Imports concretos de infraestructura o responsabilidades de endpoint |
| `infrastructure/` | Clases concretas que implementan puertos de dominio con SQL, HTTP, AWS, colas o ficheros | Reglas de negocio, decisiones de validación u orquestación de aplicación |
| `endpoints/` / `handler/` | Rutas FastAPI, esquemas request/response, wiring de dependencias, mapeo de excepciones a HTTP | Lógica de negocio o manipulación directa de entidades de dominio más allá del mapeo |

## Regla de dependencia

```text
handler/endpoints -> application -> domain <- infrastructure
```

`infrastructure/` puede importar `domain/` para implementar puertos.
`application/` debe depender de interfaces, no de adaptadores concretos.
`handler/` puede instanciar adaptadores e inyectarlos en casos de uso.

## Ejemplos

Mal: dominio importando boto3.

```python
# domain/llm_service.py
import boto3
```

Bien: dominio define el contrato e infraestructura lo implementa.

```python
# domain/llm_service.py
from abc import ABC, abstractmethod


class LlmService(ABC):
    @abstractmethod
    def make_request(self, prompt: str) -> dict:
        raise NotImplementedError  # pragma: no cover
```

```python
# infrastructure/bedrock_llm_service.py
import boto3

from ..domain.llm_service import LlmService


class BedrockLlmService(LlmService):
    def make_request(self, prompt: str) -> dict:
        ...
```

Mal: aplicación importando infraestructura concreta.

```python
from ..infrastructure.bedrock_llm_service import BedrockLlmService
```

Bien: aplicación recibe la interfaz.

```python
from ..domain.llm_service import LlmService


def extract_fields(*, llm: LlmService, document_type: str):
    ...
```

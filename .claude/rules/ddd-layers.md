# Capas DDD — qué contiene y qué no puede contener cada capa

## Tabla de capas

| Capa | Contiene | NUNCA puede contener |
|---|---|---|
| `domain/` | Entidades Pydantic (`ParsedField`, `ModelFields`...), puertos ABC con `@abstractmethod` o `raise NotImplementedError`, value objects frozen, excepciones de negocio, constantes de dominio | `import boto3`, `import sqlalchemy`, `import fastapi`, `import requests`, cualquier librería de infraestructura o framework. Cero dependencias externas. |
| `application/` | Funciones que orquestan puertos: reciben interfaces ABC como parámetros, llaman a sus métodos, coordinan el flujo | `from ..infrastructure.bedrock_llm_service import ...` o cualquier import de `infrastructure/`. Solo importa de `domain/`. |
| `infrastructure/` | Clases concretas que heredan de un puerto ABC: `BedrockLlmService(LlmService)`, `FileServiceS3(FileService)`, `SqlAlchemyDataRepository(DataRepository)`... | Lógica de negocio, reglas de validación de dominio, decisiones sobre qué hacer con los datos. Solo implementa el "cómo", no el "qué". |
| `endpoints/` | FastAPI app y rutas, esquemas Pydantic de entrada/salida, wiring (instanciar adaptadores e inyectarlos en casos de uso), mapeo `except DomainException → HTTPException` | Lógica de negocio, llamadas directas a `infrastructure/` que no pasen por un caso de uso. |

## Regla de dependencia

```
endpoints → application → domain ← infrastructure
```

La única flecha que va "hacia la derecha" desde infrastructure es que
implementa contratos definidos en domain. Nadie importa de infrastructure
excepto endpoints.

## Ejemplos reales

**MAL — dominio importando boto3:**
```python
# domain/llm_service.py  ← VIOLACIÓN
import boto3
```

**BIEN — dominio define el contrato, infrastructure lo implementa:**
```python
# domain/llm_service.py
from abc import ABC
class LlmService(ABC):
    def make_request(self, ...) -> Dict[str, Any]:
        raise NotImplementedError

# infrastructure/bedrock_llm_service.py
import boto3
from ..domain.llm_service import LlmService
class BedrockLlmService(LlmService):  
    def make_request(self, ...) -> Dict[str, Any]: ...
```

**MAL — caso de uso importando adaptador concreto:**
```python
# application/use_cases.py  ← VIOLACIÓN
from ..infrastructure.bedrock_llm_service import BedrockLlmService
def extract_fields(llm: BedrockLlmService, ...):  
```

**BIEN — caso de uso recibe la interfaz:**
```python
# application/use_cases.py
from ..domain.llm_service import LlmService
def extract_fields(llm: LlmService, ...): 
```

## Controles PSI-12

- Los adaptadores de `infrastructure/` leen credenciales exclusivamente desde
  variables de entorno o parámetros de configuración inyectados — nunca
  hardcodeadas en el código.
- `domain/` y `application/` no deben contener ninguna referencia a claves
  de API, tokens, IDs de cuenta AWS ni URLs de producción.
- Los tests de `infrastructure/` usan credenciales ficticias mediante el
  fixture `aws_credentials` (ver `setup-aws-mock`). Nunca credenciales reales.

## Automatización de estas reglas

- **En cada edición**: `.claude/hooks/check-imports.sh` verifica las
  cuatro reglas automáticamente (exit 2 si hay violación).
- **Manualmente o en PR**: `/check-import-boundaries` genera el informe
  estructurado para el `reviewer-agent`.

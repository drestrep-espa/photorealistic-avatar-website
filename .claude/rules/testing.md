# Tests — guía del proyecto §5

**Regla de oro nº 2: el código sin test no está terminado.**
Por cada fichero nuevo o modificado en `<capa>/`, debe existir o actualizarse
`tests/<capa misma ruta>/`.

## Ciclo TDD obligatorio

```
Red   → escribe primero el test que falla (describe el comportamiento deseado)
Green → escribe el mínimo código que lo hace pasar
Refactor → limpia sin cambiar comportamiento; los tests protegen
```

No escribir implementación antes de tener un test que falle.

## Pirámide de tests — qué tipo va en cada capa

| Capa | Tipo de test | Dependencias externas | Herramienta |
|---|---|---|---|
| `tests/domain/` | Unitario puro | Ninguna — sin red, sin BD, sin AWS | pytest |
| `tests/application/` | Unitario con Fakes | Fakes de los puertos, nunca adaptadores reales | pytest + Fakes |
| `tests/infrastructure/` | Integración controlada | moto (AWS mock), BD de test | pytest + moto/setup-aws-mock |
| `tests/e2e/` | E2E / integración | App completa con TestClient | pytest + FastAPI TestClient |

Muchos tests abajo (domain/application), pocos arriba (endpoints).

## Fakes — nunca MagicMock en domain/ ni application/

Un Fake hereda del puerto real. Si el contrato cambia, el Fake deja de
compilar y el test rompe (eso es correcto — te avisa del cambio).

```python
# BIEN: Fake hereda del puerto
class FakeFileService(FileService):
    def __init__(self):
        self._store: dict[str, bytes] = {}

    def download(self, key: str) -> bytes:
        if key not in self._store:
            raise FileNotFoundException
        return self._store[key]

    def upload(self, key: str, content: bytes) -> None:
        self._store[key] = content
```

```python
# MAL: mock anónimo — no detecta cambios de contrato
llm = MagicMock()
llm.make_request.return_value = {...}
```

Usa `MagicMock` solo en `tests/endpoints/` para dependencias de
infraestructura fuera del dominio (ej: UowSqlAlchemy en tests e2e).

## Object Mothers — datos de prueba reutilizables

Función que devuelve un objeto válido por defecto y permite sobreescribir
solo lo que importa al test concreto:

```python
def parsed_field_object_mother(
    field_name: str = "nombre",
    field_value: str = "Juan García",
    document_type: str = "escrituras",
    is_deidentifiable: bool = True,
) -> ParsedField:
    return ParsedField(
        field_name=field_name,
        field_value=field_value,
        document_type=document_type,
        is_deidentifiable=is_deidentifiable,
    )
```

El test solo declara lo que le importa; si la entidad cambia, se actualiza
el mother una vez, no cincuenta tests.

## Fixtures — cómo combinarlos con Fakes y Object Mothers

Usa fixtures de pytest para inyectar Fakes y datos de prueba compartidos
entre tests del mismo módulo. La regla es: **el Object Mother crea el dato,
el fixture lo inyecta**.

```python
# tests/application/conftest.py
import pytest
from tests.fakes.fake_file_service import FakeFileService
from tests.fakes.fake_llm_service import FakeLlmService
from tests.mothers.parsed_field_mother import parsed_field_object_mother

@pytest.fixture
def fake_file_service() -> FakeFileService:
    return FakeFileService()

@pytest.fixture
def fake_llm_service() -> FakeLlmService:
    return FakeLlmService()

@pytest.fixture
def valid_parsed_field():
    return parsed_field_object_mother()
```

```python
# tests/application/test_extract_fields.py
def test_extract_fields_returns_parsed_fields(fake_llm_service, fake_file_service):
    result = extract_fields(
        llm=fake_llm_service,
        file_service=fake_file_service,
        document_type="escrituras",
    )
    assert result.document_type == "escrituras"
```

**Dónde viven los fixtures:**

| Scope | Ubicación | Cuándo usarlo |
|---|---|---|
| Compartido por toda la suite | `tests/conftest.py` | Fakes genéricos reutilizables en varias capas |
| Compartido por una capa | `tests/<capa>/conftest.py` | Fakes y datos específicos de esa capa |
| Solo un módulo | mismo fichero de test | Fixtures muy específicos de un test concreto |

## Controles PSI-12

- Los Object Mothers nunca deben usar datos reales de producción (PII,
  identificadores reales de clientes, credenciales, direcciones reales).
  Usar siempre valores sintéticos y claramente ficticios.
- Los tests de `infrastructure/` que usen `moto` deben incluir el fixture
  `aws_credentials` para garantizar que ninguna llamada escape al mock.
  Ver `/setup-aws-mock` para el patrón correcto.
- No usar `scope="session"` en fixtures con estado mutable (BD con filas,
  buckets con objetos) — garantiza aislamiento entre tests.

## Automatización de estos patrones

- `/scaffold-fake` — genera `Fake<Puerto>` listo para usar en tests.
- `/scaffold-object-mother` — genera `<entidad>_object_mother` con la
  convención de función y parámetros nombrados con valores representativos.
- `/run-layer-tests <capa>` — ejecuta los tests de una capa concreta.
- `/setup-aws-mock` — configura el fixture `aws_credentials` + `moto`.


# Tests

El código sin tests no está terminado. Por cada fichero nuevo o modificado bajo
una capa, añade o actualiza los tests espejo en `tests/<misma ruta de capa>/`.

## Ciclo TDD

```text
Red -> escribe un test que falla y describe el comportamiento deseado.
Green -> implementa el mínimo código que lo hace pasar.
Refactor -> limpia mientras los tests protegen el comportamiento.
```

No escribas implementación de producción antes del test que falla, salvo que el
usuario pida explícitamente un spike.

## Pirámide de tests

| Capa | Tipo de test | Dependencias externas | Herramientas |
|---|---|---|---|
| `tests/domain/` | Unitario puro | Ninguna | pytest |
| `tests/application/` | Unitario con Fakes | Solo Fakes de puertos de dominio | pytest |
| `tests/infrastructure/` | Integración controlada | moto, BD de test, dobles locales | pytest, moto/localstack |
| `tests/e2e/`, `tests/endpoints/`, `tests/handler/` | Integración de endpoint | App completa con dependencias controladas | pytest, FastAPI TestClient |

Mantén muchos tests en dominio/aplicación y menos tests en endpoint/e2e.

## Fakes

Usa clases `Fake<Port>` que hereden del puerto de dominio real. Si la firma del
puerto cambia, el Fake debe romper de forma visible.

```python
class FakeFileService(FileService):
    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    def download(self, key: str) -> bytes:
        if key not in self._store:
            raise FileNotFoundException(key)
        return self._store[key]

    def upload(self, key: str, content: bytes) -> None:
        self._store[key] = content
```

No uses `MagicMock`, `Mock` anónimo ni `@patch` en tests de `domain/` o
`application/`. Usa mocks solo en tests de endpoint/infraestructura cuando el
mock representa un sistema externo o una frontera de framework.

## Object Mothers

Un Object Mother crea un objeto válido por defecto y permite que los tests
sobrescriban solo los campos relevantes.

```python
def parsed_field_object_mother(
    field_name: str = "nombre",
    field_value: str = "Juan Garcia",
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

El test debe declarar solo el detalle que le importa. Si la entidad cambia,
actualiza el mother una sola vez.

## Fixtures

Usa fixtures de pytest para inyectar Fakes y datos de prueba compartidos.

| Scope | Ubicación | Uso |
|---|---|---|
| Toda la suite | `tests/conftest.py` | Fakes genéricos reutilizados entre capas |
| Una capa | `tests/<capa>/conftest.py` | Fakes y datos específicos de capa |
| Un módulo | Fichero de test | Setup muy local |

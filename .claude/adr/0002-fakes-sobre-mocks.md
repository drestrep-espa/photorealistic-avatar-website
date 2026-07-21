---
id: "0002"
titulo: Fakes con herencia sobre mocks anónimos en tests de dominio y aplicación
estado: Aceptada
---

# ADR 0002 — Fakes sobre Mocks

## Contexto

Los tests de `domain/` y `application/` necesitan sustituir adaptadores
concretos (repositorios, servicios LLM, servicios de ficheros). La opción
más rápida es `MagicMock`, pero tiene un riesgo: si el puerto cambia su
firma, el mock sigue compilando y el test pasa aunque el contrato esté roto.

## Decision

Prohibir `MagicMock` y `@patch` en tests de `domain/` y `application/`.
En su lugar, usar `Fake<Puerto>` — clases Python en memoria que heredan
del puerto ABC real:

```python
class FakeFileService(FileService):
    def download(self, key: str) -> bytes: ...
    def upload(self, key: str, content: bytes) -> None: ...
```

El Fake permite `MagicMock` solo en `tests/endpoints/` para dependencias
de infraestructura fuera del dominio.

## Alternativas consideradas

1. **`MagicMock` en todos los tests** — rechazado: no detecta cambios de
   contrato. El test pasa aunque el adaptador real falle.
2. **`unittest.mock.patch`** — rechazado: acopla el test a la implementación
   interna (rutas de import), no al contrato.
3. **Tests de integración en todas las capas** — rechazado: demasiado lento
   y requiere AWS/BD levantados para tests de negocio.

## Consecuencias

- Si un puerto cambia de firma, el Fake no compila → el test rompe
  inmediatamente con un error claro (`TypeError: Can't instantiate abstract class`).
- Los tests de `domain/` y `application/` son deterministas y rápidos.
- Se requiere mantener los Fakes en `tests/fakes/` — el hook `check-imports.sh`
  detecta si algún test usa `MagicMock` en las capas prohibidas.
- `/scaffold-fake` automatiza la creación del Fake inicial.

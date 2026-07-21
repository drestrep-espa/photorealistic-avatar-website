---
name: scaffold-fake
description: Genera el esqueleto de un Fake<Interfaz> para un puerto ABC de dominio. Lee el puerto, extrae sus métodos abstractos con sus firmas completas y produce una implementación en memoria lista para usar en tests. Úsala cuando domain-agent o application-agent necesiten un doble de prueba para un puerto, o cuando el usuario pida "crea el fake de X", "genera FakeUserRepository", "necesito un doble de prueba para el puerto Y".
triggers:
  - "crea el fake de"
  - "genera Fake"
  - "doble de prueba para el puerto"
  - "scaffold-fake"
  - "fake para el puerto"
---

# Scaffold Fake

Genera un archivo con la clase `Fake<Interfaz>` — una implementación en
memoria de un puerto ABC — lista para usar en tests de dominio y aplicación.

## Argumento de entrada

El argumento es la **ruta al archivo del puerto** (interfaz ABC) cuyo Fake
se quiere generar. Ejemplos:
- `deidentify_app/src/domain/data_repository.py`
- `users/domain/user_repository.py`
- `billing/domain/notification_service.py`

Si el usuario nombra la interfaz en lugar de la ruta, localiza el archivo
con `glob` antes de continuar.

## 1. Leer y analizar el puerto

Lee el archivo del puerto. Identifica:

1. **Nombre de la clase ABC** (p. ej. `UserRepository`,
   `NotificationService`, `LlmService`).
2. **Métodos abstractos** — todos los decorados con `@abstractmethod`.
   Para cada uno extrae:
   - Nombre del método.
   - Parámetros con sus tipos exactos (incluyendo `self`).
   - Tipo de retorno (`-> <tipo>`).
   - Si es `async` o síncrono.
3. **Imports necesarios** — qué tipos usan los métodos y desde dónde se
   importan (para replicarlos en el Fake).

No inventes firmas. Si un tipo no está claro en el archivo del puerto,
léelo tal cual está y úsalo igual en el Fake.

## 2. Determinar la ruta de destino

El Fake puede vivir en dos sitios según cómo se use:

- **Un único test lo usa** → dentro del propio archivo de test, como clase
  interna. En ese caso esta skill solo genera el bloque de código para
  pegar en el test.
- **Varios tests lo reutilizan** → en un archivo dedicado en la ruta espejo
  de tests:

```
# Puerto fuente:
<dominio>/domain/user_repository.py

# Fake reutilizable:
tests/<dominio>/domain/fakes/fake_user_repository.py
# o:
tests/<dominio>/application/fakes/fake_user_repository.py
```

Detecta si ya existe un directorio `fakes/` en los tests del proyecto
(búscalo con `glob`). Si existe, úsalo. Si no, genera el código como bloque
para pegar, e indica al agente que lo ubique donde corresponda.

Si el directorio de destino no existe, créalo con `__init__.py` vacío si
el proyecto los usa.

## 3. Generar la clase Fake

Sigue este patrón estrictamente:

```python
from <ruta_del_puerto> import <NombreInterfaz>
# Importa los tipos necesarios para las firmas


class Fake<NombreInterfaz>(<NombreInterfaz>):
    """Implementación en memoria de <NombreInterfaz> para tests."""

    def __init__(self) -> None:
        # Almacén en memoria — usa el tipo más simple que soporte
        # las operaciones que los métodos necesitan:
        self.<nombre_almacen>: list[<TipoEntidad>] = []
        # Añade contadores, flags o registros de llamadas si algún
        # test necesita verificar que el método fue invocado:
        # self.calls: list[str] = []

    def <metodo1>(self, <params>) -> <tipo_retorno>:
        # Implementación mínima en memoria:
        # - save/add/create → append al almacén
        # - find/get/load → búsqueda en el almacén, devuelve None si no existe
        # - delete/remove → elimina del almacén
        # - exists/contains → bool sobre el almacén
        # - list/all → devuelve copia del almacén
        # - notify/send/publish → no hace nada (o registra en self.calls)
        ...

    def <metodo2>(self, <params>) -> <tipo_retorno>:
        ...

    # Replica TODOS los métodos abstractos del puerto, en el mismo orden.
```

### Reglas de implementación

- **Hereda del puerto real**: `class Fake<X>(<X>)`. Si el puerto cambia de
  firma, el Fake romperá en tiempo de importación — eso es exactamente lo
  que se busca.
- **Sin mocks**: no uses `unittest.mock`, `MagicMock` ni `patch`. La
  implementación es real Python en memoria.
- **Mínima pero completa**: implementa todos los `@abstractmethod`. El
  cuerpo puede ser `pass` o `return None` si el test no necesita más, pero
  nunca `raise NotImplementedError` (eso convertiría el Fake en un ABC de
  nuevo).
- **Sin lógica de negocio**: el Fake no valida reglas de dominio. Si un
  test necesita probar una validación, esa lógica está en la entidad, no
  en el Fake.
- **Helpers opcionales**: si los tests suelen necesitar pre-cargar datos,
  añade un método de conveniencia al Fake (fuera del contrato del puerto):

  ```python
  # Fuera del contrato — solo para setup de tests
  def seed(self, *items: <TipoEntidad>) -> None:
      self.<almacen>.extend(items)
  ```

- **Métodos async**: si el puerto tiene métodos `async def`, el Fake también
  debe declararlos como `async def`.

## 4. Verificar que implementa el contrato completo

Tras generar el archivo, comprueba que no quedan métodos abstractos sin
implementar:

```bash
<prefijo_venv>/python -c "
from <ruta_fake> import Fake<NombreInterfaz>
obj = Fake<NombreInterfaz>()
print('Contrato completo OK')
"
```

Si lanza `TypeError: Can't instantiate abstract class`, significa que falta
implementar algún método. Corrígelo antes de reportar.

## 5. Resultado

Entrega:
1. Ruta exacta del archivo generado (o indicación de que es un bloque para
   pegar en el test).
2. Lista de métodos implementados con su firma.
3. Descripción del almacén interno (qué estructura de datos usa y por qué).
4. Si hay métodos en el puerto cuya semántica no está clara (p. ej. qué
   debe devolver `find_by_id` si no existe el elemento), indica el supuesto
   adoptado (`None`, excepción, lista vacía) para que el agente lo revise.

## No Usar Cuando

Para crear mocks anónimos (`MagicMock`, `@patch`) — el proyecto prohíbe
mocks anónimos en `domain/` y `application/`. Usar siempre Fakes con
herencia del puerto real.

## Controles PSI-12

El Fake no debe contener datos reales de producción en su almacén interno.
Los valores de inicialización deben ser genéricos y claramente sintéticos.

## Referencias

- Patrón Fake: `.claude/rules/testing.md` §Fakes
- Convención de nombrado: `.claude/rules/naming.md` → `Fake<Puerto>`
- Agentes que la invocan: `domain-agent`, `application-agent`

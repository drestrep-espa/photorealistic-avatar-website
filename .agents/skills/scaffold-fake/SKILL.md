---
name: scaffold-fake
description: "Genera una implementación Fake para un puerto ABC de dominio. Lee el puerto, conserva todas las firmas de métodos abstractos y crea un doble de prueba en memoria para tests de domain/application. Úsala cuando un agente de capa necesite un Fake, cuando se cree un puerto nuevo o cuando el usuario pida crear un fake o doble para un puerto."
---

# Scaffold Fake

Genera un `Fake<Port>` reutilizable en memoria para tests.

## Workflow

1. Localiza el fichero del puerto si el usuario solo da el nombre de la
   interfaz.
2. Lee el puerto y extrae:
   - Nombre de la clase ABC.
   - Todos los `@abstractmethod`, conservando el orden.
   - Firma de cada método, anotación de retorno y si es async.
   - Tipos necesarios para las firmas.
3. Elige el destino:
   - Si existe un directorio compartido `tests/**/fakes/`, coloca ahí el Fake.
   - Si no, replica la convención de capa ya usada por los tests vecinos.
4. Genera una clase que herede del puerto real:

```python
class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._items: dict[str, User] = {}

    def save(self, user: User) -> None:
        self._items[user.id] = user
```

5. Implementa todos los métodos abstractos. Usa estructuras simples en memoria:
   - save/add/create -> append o asignación.
   - find/get/load -> búsqueda, devolviendo la convención del proyecto (`None`
     o excepción).
   - delete/remove -> eliminación.
   - exists/contains -> bool.
   - list/all -> copia de la colección.
   - notify/send/publish -> no-op o registro de llamadas si los tests lo
     necesitan.
6. Añade helpers de setup como `seed(...)` solo cuando sean útiles para tests.
7. Verifica que el Fake puede instanciarse:

```bash
.venv/bin/python -c "from tests.fakes.fake_user_repository import FakeUserRepository; FakeUserRepository(); print('OK')"
```

## Reglas

- Nunca uses `MagicMock`, `Mock` anónimo ni `patch`.
- Nunca dejes métodos abstractos sin implementar.
- No añadas validación de negocio al Fake.
- Conserva los métodos async como `async def`.

## Resultado

Reporta la ruta del fichero, los métodos implementados con sus firmas, el
almacén interno y cualquier supuesto sobre comportamiento ante elementos
inexistentes.

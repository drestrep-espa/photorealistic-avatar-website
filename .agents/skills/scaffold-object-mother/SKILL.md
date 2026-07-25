---
name: scaffold-object-mother
description: "Genera un Object Mother para una entidad de dominio. Lee la entidad, extrae campos y factory methods, y crea un helper de test que devuelve objetos válidos por defecto con overrides concretos. Úsala al crear una entidad nueva, escribir tests de domain/application o cuando el usuario pida datos de prueba u object mother."
---

# Scaffold Object Mother

Genera un Object Mother que crea objetos de dominio válidos por defecto.

## Workflow

1. Localiza el fichero de la entidad si el usuario solo da el nombre.
2. Lee la entidad y extrae:
   - Nombre de clase.
   - Campos y anotaciones.
   - Campos obligatorios frente a opcionales.
   - Factory methods como `from_raw_data`.
   - Restricciones de validación existentes.
3. Elige un destino que replique las convenciones de tests existentes,
   normalmente:

```text
tests/<module>/domain/<entity>_object_mother.py
```

4. Genera un helper usando la factoría de la entidad cuando exista:

```python
def user_object_mother(
    user_id: str = "user-1",
    email: str = "user@example.com",
    active: bool = True,
) -> User:
    return User.from_raw_data(
        {
            "user_id": user_id,
            "email": email,
            "active": active,
        }
    )
```

5. Usa defaults estables y representativos:
   - `str`: texto de ejemplo significativo.
   - `int`: `1` o el mínimo valor válido.
   - `float`: `1.0`.
   - `bool`: el valor válido más común.
   - `UUID`: un UUID fijo.
   - `datetime`: un datetime fijo, nunca `now()`.
   - `Enum`: el primer enum válido salvo que el contexto sugiera otro.
   - `list`: `[]` salvo que la entidad requiera elementos.
6. Verifica que el helper importa y construye una entidad.

## Reglas

- No uses `None` como default salvo que el campo sea genuinamente opcional.
- No evites la validación de la entidad.
- Añade parámetros de override solo para campos obligatorios/simples o campos
  que los tests suelan variar.

## Resultado

Reporta la ruta del fichero, las funciones helper generadas y cualquier campo
complejo que se haya dejado intencionadamente sin helper de override.

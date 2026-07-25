---
name: run-layer-tests
description: "Ejecuta pytest para una capa de Arquitectura Hexagonal dentro del entorno virtual del proyecto. Úsala para tests de domain, application, infrastructure, handler, endpoints, e2e o all, y cuando el usuario pida ejecutar tests de una capa concreta. Requiere un entorno Python verificado; invoca python-sandbox primero si hace falta."
---

# Ejecutar tests por capa

Ejecuta solo la capa de tests solicitada, salvo que el usuario pida `all`.

## Entradas

Nombres de capa aceptados:

| Argumento | Patrón de ruta de tests |
|---|---|
| `domain` | `tests/**/domain/**` |
| `application` | `tests/**/application/**` |
| `infrastructure` | `tests/**/infrastructure/**` |
| `handler` | `tests/**/handler/**` |
| `endpoints` | `tests/**/endpoints/**` |
| `e2e` | `tests/**/e2e/**` |
| `all` | `tests/` |

Pregunta solo si la capa solicitada es realmente ambigua.

## Flujo

1. Verifica el venv y pytest. Si faltan, usa `$python-sandbox`.
2. Localiza ficheros `test_*.py` bajo el patrón de la capa solicitada.
3. Si no existen tests para esa capa, repórtalo claramente y detente.
4. Ejecuta pytest a través del venv:

```bash
.venv/bin/python -m pytest <paths> -v --tb=short
```

En Windows, usa `.venv/Scripts/python.exe -m pytest`.

No uses `--exitfirst` salvo que se pida explícitamente.

Para tests de infraestructura que usen contenedores o dobles externos lentos,
añade timeout si el proyecto ya usa un plugin de timeout.

## Resultado

Devuelve:

```text
Tests de <capa> - <rutas>
Resultado: X pasados | Y fallidos | Z errores
Tiempo: <duración>
```

Si hay fallos, lista cada test fallido y la línea de error relevante. Si hay
errores de colección, repórtalos antes que los fallos de aserción.

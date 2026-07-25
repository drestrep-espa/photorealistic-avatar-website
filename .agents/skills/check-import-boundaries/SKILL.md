---
name: check-import-boundaries
description: "Verifica las fronteras de imports de Arquitectura Hexagonal en proyectos Foqum. Úsala para detectar domain importando infraestructura/frameworks, application importando adaptadores concretos, infrastructure importando application, handlers importando entidades de dominio o uso de MagicMock en tests de domain/application."
---

# Comprobar fronteras de imports

Ejecuta el checker determinista usado por los hooks de Codex:

```bash
bash .codex/hooks/check-imports.sh
```

Si el comando se ejecuta desde un subdirectorio, resuelve primero la raíz del
proyecto o lánzalo desde la raíz del workspace.

## Qué verifica

- `domain/` no debe importar `application/`, `infrastructure/`, `endpoints/` ni
  `handler/`.
- `domain/` no debe importar librerías de infraestructura/framework como
  SQLAlchemy, boto3, FastAPI, requests, httpx, Redis o Celery.
- `application/` no debe importar `infrastructure/`.
- `infrastructure/` no debe importar `application/`.
- `handler/` y `endpoints/` no deben importar entidades ni puertos de dominio
  directamente. Las excepciones de dominio sí están permitidas para mapeo HTTP.
- `tests/**/domain/**` y `tests/**/application/**` no deben usar mocks anónimos.

## Resultado

Si el checker falla, reporta cada violación con fichero, línea, regla rota y el
agente/rol que debería corregirla.

---
name: pr-checklist
description: "Ejecuta el checklist completo Foqum previo al PR. Úsala cuando una funcionalidad o corrección esté terminada y antes de abrir o marcar como listo un Pull Request. Ejecuta tests completos, cobertura, comprobación de fronteras de imports, checklist manual de arquitectura, lint y tipos. No usar durante desarrollo incremental normal salvo petición explícita."
---

# Checklist PR

Ejecuta estos pasos en orden. Si falla una comprobación obligatoria, detente y
corrige antes de marcar la tarea como terminada.

## 1. Tests completos

Usa `$run-layer-tests all`, o ejecuta:

```bash
.venv/bin/python -m pytest tests/ -v --tb=short
```

Si el entorno no está listo, usa primero `$python-sandbox`.

## 2. Cobertura

Usa `$coverage-gate`.

## 3. Fronteras de imports

Usa `$check-import-boundaries`.

## 4. Checklist de revisión manual

Verifica:

- El cambio está en la capa correcta.
- Dominio no tiene dependencias SQL, HTTP, AWS ni de framework.
- Los casos de uso reciben interfaces ABC, no implementaciones concretas.
- La lógica de negocio no está en endpoints/handlers ni en adaptadores.
- Los adaptadores nuevos usan prefijo de tecnología.
- Los tests están en la ruta espejo y usan Fakes/Object Mothers donde toca.
- Los tests de domain/application no usan mocks anónimos.
- Las nuevas excepciones de negocio heredan de `Exception` y viven en
  `domain/exceptions.py`, salvo que el proyecto local use otra convención.
- El cambio es mínimo y sigue los ficheros vecinos.

## 5. Lint y tipos

Prefiere los comandos locales del proyecto. Si no hay ninguno definido, prueba:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy .
```

Si mypy no está configurado o instalado, repórtalo en lugar de inventar un
configuración nueva de tipado.

## Resultado

Devuelve una tabla compacta con `PASS`, `FAIL` o `SKIP` para cada paso, además
del detalle de fichero/línea necesario para corregir fallos.

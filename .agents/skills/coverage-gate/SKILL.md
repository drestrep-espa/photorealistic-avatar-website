---
name: coverage-gate
description: "Ejecuta el gate de cobertura Foqum para tests Python. Úsala antes de marcar una tarea como lista para PR, cuando el usuario pida comprobar cobertura o cuando haya que validar que la cobertura no cae por debajo del umbral configurado."
---

# Gate de cobertura

Ejecuta:

```bash
python3 .codex/hooks/coverage-gate.py
```

El gate usa el venv del proyecto si existe. Lee umbrales de cobertura desde
`pyproject.toml`, `.coveragerc` o `setup.cfg`; si no hay configuración, usa 80
por ciento.

Esta versión para Codex no instala dependencias automáticamente y no ejecuta
`git stash`. Si falta pytest, pytest-cov o el venv, ejecuta primero
`$python-sandbox`.

## Resultado

Reporta:

- Cobertura actual.
- Umbral.
- Resumen de fallo de tests si falla pytest.
- Módulos por debajo del 70 por ciento de cobertura.
- Si el gate pasa o falla.

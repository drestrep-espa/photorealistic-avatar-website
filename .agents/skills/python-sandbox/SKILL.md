---
name: python-sandbox
description: "Prepara o verifica un entorno virtual Python aislado para el proyecto actual. Detecta o crea el venv, instala dependencias y verifica pytest/ruff. Úsala antes de ejecutar pytest, linters, cobertura, mypy o cualquier herramienta Python del proyecto, y cuando el usuario pida preparar el entorno, crear el venv o instalar dependencias."
---

# Sandbox Python

Prepara un entorno virtual Python sin depender de la activación persistente de
la shell.

## Flujo

1. Localiza la raíz del proyecto subiendo hasta el primer directorio que
   contenga uno de estos ficheros:
   `pyproject.toml`, `setup.py`, `setup.cfg` o `requirements.txt`.
2. Detecta un venv existente en este orden: `.venv/`, `venv/`, `env/`.
3. Si no existe ninguno, crea `.venv` con `python -m venv .venv`, usando
   `python3 -m venv .venv`.
4. Usa directamente el ejecutable del venv:
   - Unix: `.venv/bin/python`
   - Windows: `.venv/Scripts/python.exe`
5. Instala dependencias desde la mejor fuente disponible:
   - `pyproject.toml`: prueba `-e ".[dev,test]"`, después `-e ".[dev]"`,
     después `-e ".[test]"` y finalmente `-e .`.
   - `requirements-dev.txt` o `requirements-test.txt`.
   - `requirements.txt`.
6. Verifica herramientas:
   - `<python> -m pytest --version`
   - `<python> -m ruff --version`
7. Si falta pytest o ruff, instala `pytest ruff`.

No continúes con tests o linters si falla la preparación del entorno. Reporta
el comando exacto y el error.

## Resultado

Reporta:

```text
- Entorno listo:
- Venv: .venv/ (nuevo o existente)
- Python: <versión>
- Dependencias: <fuente>
- Pytest: <versión>
- Ruff: <versión>
- Comando Python: <ruta>
```

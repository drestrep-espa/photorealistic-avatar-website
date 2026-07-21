---
name: python-sandbox
description: Prepara un entorno virtual Python aislado para el proyecto actual. Detecta o crea el venv, instala dependencias y verifica que el entorno está listo para ejecutar tests o herramientas. Úsala antes de ejecutar pytest, linters o cualquier herramienta Python del proyecto. También úsala cuando el usuario pida "prepara el entorno", "crea el venv", "instala dependencias" o similar.
triggers:
  - "prepara el entorno"
  - "crea el venv"
  - "instala dependencias"
  - "python-sandbox"
  - "configura el entorno Python"
---

# Python Sandbox

Prepara un entorno virtual Python aislado y con dependencias instaladas.
El objetivo es que cualquier comando posterior (pytest, ruff, cobertura) se
ejecute dentro de este entorno sin contaminar el Python del sistema.

## 1. Localizar la raíz del proyecto

Busca el archivo de configuración del proyecto subiendo desde el directorio
actual hasta encontrar uno de estos archivos (en orden de prioridad):

1. `pyproject.toml`
2. `setup.py`
3. `setup.cfg`
4. `requirements.txt`

Ese directorio es la **raíz del proyecto**. Todos los comandos siguientes se
ejecutan desde ahí. Si no encuentras ninguno, detente y pide al usuario que
confirme cuál es la raíz.

## 2. Detectar o crear el venv

Busca un entorno virtual existente en este orden:
- `.venv/`
- `venv/`
- `env/`

Si existe uno, úsalo. Si no existe ninguno, créalo:

```bash
python -m venv .venv
```

Si `python` no está disponible, prueba con `python3`. Si ninguno funciona,
detente y reporta al usuario qué comando de Python está disponible en el
sistema (`where python`, `where python3`).

## 3. Determinar el prefijo de activación

No actives el venv con `source activate` ni con `activate.bat` — esos comandos
no persisten entre llamadas a Bash. En su lugar, usa el ejecutable del venv
directamente como prefijo en todos los comandos:

**En Windows (PowerShell o cmd):**
```
.venv\Scripts\python
.venv\Scripts\pip
.venv\Scripts\pytest
.venv\Scripts\ruff
```

**En Linux / macOS:**
```
.venv/bin/python
.venv/bin/pip
.venv/bin/pytest
.venv/bin/ruff
```

Detecta el sistema operativo con:
```bash
python -c "import sys; print(sys.platform)"
```

Guarda el prefijo correcto como variable de trabajo para usarlo en los pasos
siguientes de esta skill y comunicarlo al resultado final.

## 4. Instalar dependencias

Actualiza pip primero para evitar warnings:
```bash
<prefijo_python> -m pip install --upgrade pip --quiet
```

Luego instala según lo que encuentres en la raíz del proyecto:

**Si existe `pyproject.toml`** (proyecto con build system moderno):
```bash
<prefijo_python> -m pip install -e ".[dev,test]" --quiet
```
Si el extra `[dev,test]` falla (no está definido), intenta con `[dev]`, luego
con `[test]`, y por último sin extras:
```bash
<prefijo_python> -m pip install -e . --quiet
```

**Si existe `requirements-dev.txt` o `requirements-test.txt`**:
```bash
<prefijo_pip> install -r requirements-dev.txt --quiet
# o
<prefijo_pip> install -r requirements-test.txt --quiet
```

**Si solo existe `requirements.txt`**:
```bash
<prefijo_pip> install -r requirements.txt --quiet
```

Si ninguno de los anteriores funciona, detente y muestra al usuario los
archivos de configuración que encontraste para que decida cómo proceder.

## 5. Verificar que el entorno está listo

Comprueba que las herramientas principales están disponibles:
```bash
<prefijo_python> -m pytest --version
<prefijo_python> -m ruff --version
```

Si alguna falta (ImportError o comando no encontrado), instálala:
```bash
<prefijo_pip> install pytest ruff --quiet
```

## 6. Resultado

Informa al usuario con un resumen conciso:

```
Entorno listo:
- Venv: .venv/ (nuevo / existente)
- Python: <versión>
- Dependencias: instaladas desde <pyproject.toml / requirements-dev.txt / ...>
- Pytest: <versión>
- Ruff: <versión>
- Prefijo para comandos: .venv/Scripts/  (Windows) o .venv/bin/ (Unix)
```

Si en cualquier paso algo falla, reporta el error exacto y detente — no
continúes con pasos siguientes sobre un entorno roto.

## No Usar Cuando

Si el venv ya existe y está operativo (`.venv/Scripts/python --version`
responde). No recrear sin motivo — las dependencias ya instaladas se perderían.

## Controles PSI-12

No instalar paquetes de fuentes no verificadas. Usar solo los extras
definidos en `pyproject.toml` o los archivos `requirements*.txt` del proyecto.
No escribir credenciales en el venv ni en ningún fichero de configuración
generado durante la instalación.

## Referencias

- Depende de: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`
- Requerida por: `run-layer-tests`, `coverage-gate`, `pr-checklist`

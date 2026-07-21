---
name: run-layer-tests
description: Ejecuta pytest para una capa específica de la arquitectura hexagonal (domain, application, infrastructure, handler/e2e) dentro del entorno virtual del proyecto. Úsala cuando un subagente necesite correr los tests de su capa, o cuando el usuario pida "pasa los tests de dominio", "ejecuta los tests de aplicación", "corre los tests de infraestructura", "lanza los e2e", etc. Requiere que el entorno virtual esté preparado (invoca python-sandbox si no lo está).
triggers:
  - "pasa los tests de dominio"
  - "ejecuta los tests de aplicación"
  - "corre los tests de infraestructura"
  - "lanza los e2e"
  - "run-layer-tests"
  - "tests de la capa"
---

# Run Layer Tests

Ejecuta la suite de tests de una capa concreta de la arquitectura hexagonal
del proyecto dentro del entorno virtual del proyecto. Nunca lanza tests de
otras capas — el alcance acotado es intencional.

## 0. Argumento de entrada

El argumento de esta skill es la **capa** a testear. Valores aceptados:

| Argumento | Ruta de tests | Descripción |
|---|---|---|
| `domain` | `tests/**/domain/**` | Tests de entidades, value objects, puertos, excepciones |
| `application` | `tests/**/application/**` | Tests de casos de uso con Fakes |
| `infrastructure` | `tests/**/infrastructure/**` | Tests de adaptadores con servicios simulados |
| `handler` o `e2e` | `tests/**/e2e/**` o `tests/**/handler/**` | Tests de integración de endpoints |
| `all` | `tests/` | Suite completa (solo invocar desde reviewer-agent) |

Si el argumento no está claro en el mensaje del usuario o del agente que
invoca la skill, pregunta antes de ejecutar.

## 1. Verificar el entorno virtual

Comprueba que existe `.venv/` (o `venv/` o `env/`) en la raíz del proyecto y
que `pytest` está disponible dentro:

```bash
# Windows
.venv\Scripts\pytest --version

# Unix
.venv/bin/pytest --version
```

Si no está disponible, **invoca la skill `python-sandbox`** antes de
continuar. No continúes sobre un entorno roto.

## 2. Detectar la ruta de tests correcta

Antes de ejecutar, verifica que la ruta de tests existe:

```bash
# Comprueba si hay archivos de test para la capa pedida
```

Usa `glob` para encontrar los archivos `test_*.py` en la ruta esperada.
Si no hay ninguno, avisa al usuario ("No se encontraron tests para la capa
`<capa>` en `tests/**/domain/**`") y detente — no falles silenciosamente.

Si el proyecto usa una estructura de tests diferente a `tests/**/`, detéctala
buscando el directorio que contenga archivos `test_*.py` desde la raíz.

## 3. Ejecutar pytest

Usa el ejecutable del venv con estos flags base:

```bash
# Windows
.venv\Scripts\pytest <ruta_de_tests> -v --tb=short

# Unix
.venv/bin/pytest <ruta_de_tests> -v --tb=short
```

Flags explicados:
- `-v` — output detallado (nombre de cada test + PASSED/FAILED).
- `--tb=short` — traceback compacto en caso de fallo (suficiente para
  identificar el problema sin ruido).

**No uses** `--exitfirst` / `-x` salvo que el agente invocante lo pida
explícitamente — queremos ver todos los fallos, no solo el primero.

### Flags adicionales por capa

**`infrastructure`**: si el proyecto usa `pytest-docker` o fixtures de
contenedor, añade `--timeout=60` para evitar que un contenedor lento cuelgue
la ejecución indefinidamente.

**`e2e` / `handler`**: añade `-p no:warnings` si los warnings de FastAPI /
Starlette ensucian el output (solo si ya están suprimidos en el repo — mira
`pyproject.toml` sección `[tool.pytest.ini_options]`).

## 4. Interpretar el resultado

Lee el resumen final de pytest (`X passed, Y failed, Z errors`) y clasifica:

- **Todo pasa** → informa brevemente: `Tests de <capa>: X passed ✓`
- **Hay fallos** → lista cada test fallido con su nombre y el mensaje de
  error relevante (extrae de `--tb=short`). No abrevies ni ocultes fallos.
- **Hay errores de colección** (ImportError, SyntaxError antes de ejecutar)
  → son más graves que fallos: el test ni siquiera pudo cargarse. Repórtalos
  primero y separados de los fallos de aserción.

## 5. Resultado

Entrega siempre:

```
Tests de <capa> — <ruta ejecutada>

Resultado: X passed | Y failed | Z errors
Tiempo: <duración total>

<Si hay fallos o errores, lista cada uno>:
  - FAILED tests/domain/test_user.py::test_user_se_crea_activo
    AssertionError: expected active=True, got active=False

<Si todo pasa>:
  Suite limpia. Puede continuar.
```

Si el agente invocante es `reviewer-agent` y hay fallos, añade al final:
```
Reasignar corrección a: <domain-agent | application-agent | infrastructure-agent | handler-agent>
```
según la capa donde se encuentren los tests fallidos.

## No Usar Cuando

Para correr tests de una capa diferente a la del agente que invoca la skill.
Cada agente ejecuta solo su capa. El argumento `all` está reservado
exclusivamente para `reviewer-agent` — ningún agente de capa debe usarlo.

## Controles PSI-12

Los tests de `infrastructure/` con `moto` no deben usar credenciales reales.
Si un test falla con `botocore.exceptions.NoCredentialsError`, usar
`/setup-aws-mock` para configurar las credenciales ficticias correctamente.

## Referencias

- Requiere: `python-sandbox` (si el venv no está listo)
- Reglas de tests: `.claude/rules/testing.md`
- Agentes que la invocan: `domain-agent`, `application-agent`,
  `infrastructure-agent`, `handler-agent`, `reviewer-agent`

---
name: coverage-gate
description: Ejecuta pytest con cobertura, extrae el porcentaje total y falla con mensaje claro si la cobertura bajó respecto al umbral del proyecto o al estado anterior. Úsala cuando reviewer-agent ejecute el punto 8 del checklist, o cuando el usuario pida "comprueba la cobertura", "verifica que no bajó la cobertura", "pasa el gate de cobertura".
triggers:
  - "comprueba la cobertura"
  - "verifica que no bajó la cobertura"
  - "pasa el gate de cobertura"
  - "coverage-gate"
  - "mide la cobertura"
---

# Coverage Gate

Ejecuta la suite completa con medición de cobertura y determina si el
resultado es aceptable según el umbral del proyecto. Produce un informe
listo para el punto 8 del checklist de `reviewer-agent`.

## 1. Verificar el entorno virtual

Comprueba que `pytest-cov` está disponible:

```bash
<prefijo_venv>/python -m pytest --co -q 2>&1 | head -3
<prefijo_venv>/python -c "import pytest_cov; print('pytest-cov', pytest_cov.__version__)"
```

Si no está instalado:
```bash
<prefijo_venv>/pip install pytest-cov --quiet
```

## 2. Detectar la configuración de cobertura existente

Busca si el proyecto ya tiene cobertura configurada:

```bash
# En pyproject.toml
grep -A 10 "\[tool.coverage" pyproject.toml 2>/dev/null

# En setup.cfg
grep -A 10 "\[coverage:" setup.cfg 2>/dev/null

# En .coveragerc
cat .coveragerc 2>/dev/null
```

Si encuentra configuración, úsala tal cual — no la sobreescribas.
Si no hay configuración, ejecuta con las opciones mínimas del paso 3.

## 3. Ejecutar pytest con cobertura

```bash
<prefijo_venv>/python -m pytest tests/ \
  --cov=. \
  --cov-report=term-missing \
  --cov-report=json:.coverage-report.json \
  -q \
  --tb=no
```

Flags:
- `--cov=.` → mide todo el código fuente del proyecto.
- `--cov-report=term-missing` → muestra en terminal las líneas sin cubrir.
- `--cov-report=json` → guarda JSON para extraer el porcentaje exacto.
- `-q` → output compacto (no necesitamos el detalle de cada test aquí,
  solo el resumen de cobertura).
- `--tb=no` → suprime tracebacks de fallos (si hay fallos de tests, ya
  los reportó `run-layer-tests`; aquí nos interesa solo la cobertura).

Si el proyecto tiene una ruta `src/` separada, ajusta:
```bash
--cov=src/
```
Detecta esto buscando si `pyproject.toml` tiene `[tool.coverage.run] source`.

## 4. Extraer el porcentaje total

Del output de `--cov-report=term-missing`, extrae la línea `TOTAL`:

```
TOTAL    1234    89    93%
```

El último valor (`93%`) es el porcentaje total de cobertura.

Alternativamente, del JSON generado:
```bash
<prefijo_venv>/python -c "
import json
with open('.coverage-report.json') as f:
    data = json.load(f)
print(f\"{data['totals']['percent_covered']:.1f}%\")
"
```

## 5. Determinar el umbral

Busca el umbral configurado en este orden:

1. **`pyproject.toml`** — `[tool.coverage.report] fail_under = <N>`
2. **`.coveragerc`** — `[report] fail_under = <N>`
3. **`setup.cfg`** — `[coverage:report] fail_under = <N>`
4. **Sin umbral configurado** → usa `80%` como mínimo razonable e
   indícalo explícitamente en el informe.

## 6. Comparar con el estado anterior

Si existe `.coverage-report.json` del estado anterior (commit/rama base),
compara:

```bash
# Si tienes acceso a git:
git stash
<prefijo_venv>/python -m pytest tests/ --cov=. --cov-report=json:.coverage-baseline.json -q --tb=no
git stash pop

# Extrae la diferencia:
<prefijo_venv>/python -c "
import json
with open('.coverage-report.json') as f:
    current = json.load(f)['totals']['percent_covered']
with open('.coverage-baseline.json') as f:
    baseline = json.load(f)['totals']['percent_covered']
diff = current - baseline
sign = '+' if diff >= 0 else ''
print(f'Actual: {current:.1f}% | Baseline: {baseline:.1f}% | Diferencia: {sign}{diff:.1f}%')
"
```

Si la comparación con git no es posible (estado de trabajo sucio, sin
historial), omite este paso e indica que no hay baseline disponible.

## 7. Limpieza

Elimina los archivos temporales generados:
```bash
# Elimina solo el JSON temporal, no .coverage (puede ser útil para el IDE)
rm -f .coverage-report.json .coverage-baseline.json
```

## 8. Resultado

### Si la cobertura supera el umbral y no bajó:

```
Cobertura: PASA
  Total: 93% (umbral: 80%)
  Diferencia vs baseline: +1.2%
  Suite: X passed, 0 failed
```

### Si la cobertura está por debajo del umbral o bajó:

```
Cobertura: FALLA
  Total: 76% (umbral: 80%) — 4 puntos por debajo
  Diferencia vs baseline: -3.1%

  Módulos con menor cobertura (< 70%):
    src/infrastructure/bedrock_llm_service.py   45%  líneas sin cubrir: 23-45, 67-89
    src/application/use_cases.py                62%  líneas sin cubrir: 112-130

  Reasignar a:
    infrastructure-agent → añadir tests para bedrock_llm_service.py
    application-agent    → añadir tests para use_cases.py
```

Incluye siempre la lista de módulos con cobertura baja (< 70%) para que
el orquestador sepa exactamente a qué agente reasignar y qué líneas cubrir.

## No Usar Cuando

Para verificar tests durante el desarrollo (usa `/run-layer-tests`).
La cobertura automática al final de cada turno la gestiona el hook
`coverage-gate.sh` — esta skill es para invocación manual o desde
`reviewer-agent`.

## Controles PSI-12

Si el informe de módulos con baja cobertura incluye adaptadores de AWS
(`infrastructure/`), priorizar su cobertura — son los puntos de mayor
riesgo de seguridad.

## Referencias

- Hook automático equivalente: `.claude/hooks/coverage-gate.sh`
- Umbral configurado en: `pyproject.toml` → `[tool.coverage.report] fail_under`
- Agente que la invoca: `reviewer-agent`

#!/usr/bin/env bash
# ============================================================
# coverage-gate.sh — Stop hook
# Se dispara cuando un agente termina su turno.
# Ejecuta pytest con cobertura y bloquea (salida 2) si la
# cobertura total bajó respecto al baseline del último commit.
# ============================================================

set -euo pipefail

# ── Guardia: saltar si no hay cambios Python en este turno ──
# Evita correr la suite completa en turnos de solo lectura.
if ! git status --porcelain 2>/dev/null | grep -q '\.py$'; then
  echo "✓ coverage-gate: sin cambios Python — saltando"
  exit 0
fi

THRESHOLD=80          # mínimo absoluto si no hay configuración en el proyecto
COVERAGE_JSON=".coverage-report-current.json"
BASELINE_JSON=".coverage-report-baseline.json"

# ── 1. Localizar el intérprete de Python del venv ───────────
# Busca en los prefijos habituales; si no encuentra ninguno usa el del sistema.
if [[ -f ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
elif [[ -f "venv/bin/python" ]]; then
  PYTHON="venv/bin/python"
elif [[ -f ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"   # Windows
else
  PYTHON="python3"
fi

# ── 2. Comprobar que pytest-cov está disponible ─────────────
if ! $PYTHON -c "import pytest_cov" 2>/dev/null; then
  echo "⚠ coverage-gate: pytest-cov no encontrado. Instalando..."
  $PYTHON -m pip install pytest-cov --quiet
fi

# ── 3. Detectar carpeta de fuentes ──────────────────────────
if [[ -d "src" ]]; then
  SOURCE_DIR="src"
else
  # Usa el primer paquete Python que encuentre en la raíz (con __init__.py)
  SOURCE_DIR=$(find . -maxdepth 1 -name "__init__.py" -exec dirname {} \; | head -1)
  SOURCE_DIR=${SOURCE_DIR:-.}
fi

# ── 4. Leer umbral del proyecto si existe ───────────────────
PROJECT_THRESHOLD=$( \
  grep -A5 "\[tool\.coverage\.report\]" pyproject.toml 2>/dev/null \
  | grep "fail_under" | grep -o "[0-9]*" | head -1 \
  || grep "fail_under" .coveragerc 2>/dev/null \
  | grep -o "[0-9]*" | head -1 \
  || echo "" \
)
if [[ -n "$PROJECT_THRESHOLD" ]]; then
  THRESHOLD=$PROJECT_THRESHOLD
fi

# ── 5. Ejecutar suite con cobertura ─────────────────────────
echo "▶ coverage-gate: ejecutando pytest con cobertura (umbral: ${THRESHOLD}%)..."

$PYTHON -m pytest tests/ \
  --cov="$SOURCE_DIR" \
  --cov-report=term-missing \
  --cov-report="json:$COVERAGE_JSON" \
  -q \
  --tb=no \
  2>&1 || true   # no abortar si hay tests fallidos (ya los reportó run-layer-tests)

# ── 6. Extraer porcentaje actual ─────────────────────────────
if [[ ! -f "$COVERAGE_JSON" ]]; then
  echo "⚠ coverage-gate: no se generó el JSON de cobertura. ¿Hay tests?"
  exit 0
fi

CURRENT=$($PYTHON -c "
import json
with open('$COVERAGE_JSON') as f:
    data = json.load(f)
print(f\"{data['totals']['percent_covered']:.1f}\")
")

# ── 7. Obtener baseline del último commit ────────────────────
BASELINE=""
if git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "  Calculando baseline desde el último commit..."
  git stash --include-untracked --quiet 2>/dev/null || true

  $PYTHON -m pytest tests/ \
    --cov="$SOURCE_DIR" \
    --cov-report="json:$BASELINE_JSON" \
    -q --tb=no 2>&1 | tail -1 || true

  git stash pop --quiet 2>/dev/null || true

  if [[ -f "$BASELINE_JSON" ]]; then
    BASELINE=$($PYTHON -c "
import json
with open('$BASELINE_JSON') as f:
    data = json.load(f)
print(f\"{data['totals']['percent_covered']:.1f}\")
")
  fi
fi

# ── 8. Módulos con cobertura baja ────────────────────────────
LOW_COVERAGE=$($PYTHON -c "
import json
with open('$COVERAGE_JSON') as f:
    data = json.load(f)
files = data.get('files', {})
low = []
for path, info in files.items():
    pct = info['summary']['percent_covered']
    if pct < 70:
        missing = info['missing_lines']
        low.append(f'  {path:<60} {pct:.0f}%  líneas: {missing[:5]}')
for line in sorted(low):
    print(line)
" 2>/dev/null || true)

# ── 9. Evaluar resultado ─────────────────────────────────────
FAILED=0
DIFF_MSG=""

# Compara contra baseline si existe
if [[ -n "$BASELINE" ]]; then
  DIFF=$($PYTHON -c "print(f'{float('$CURRENT') - float('$BASELINE'):.1f}')")
  SIGN=$(echo "$DIFF" | grep -c "^-" && echo "-" || echo "+")
  DIFF_MSG="  Baseline (último commit): ${BASELINE}%  |  Diferencia: ${DIFF}%"

  if (( $(echo "$DIFF < -1.0" | $PYTHON -c "import sys; print(int(eval(sys.stdin.read())))") )); then
    FAILED=1
  fi
fi

# Compara contra umbral absoluto
if (( $(echo "$CURRENT < $THRESHOLD" | $PYTHON -c "import sys; print(int(eval(sys.stdin.read())))") )); then
  FAILED=1
fi

# ── 10. Limpieza ─────────────────────────────────────────────
rm -f "$COVERAGE_JSON" "$BASELINE_JSON"

# ── 11. Informe ──────────────────────────────────────────────
if [[ $FAILED -eq 0 ]]; then
  echo "✓ coverage-gate: PASA"
  echo "  Cobertura total: ${CURRENT}%  (umbral: ${THRESHOLD}%)"
  [[ -n "$DIFF_MSG" ]] && echo "$DIFF_MSG"
  exit 0
else
  echo "✗ coverage-gate: FALLA"
  echo "  Cobertura total: ${CURRENT}%  (umbral: ${THRESHOLD}%)"
  [[ -n "$DIFF_MSG" ]] && echo "$DIFF_MSG"
  echo ""

  if [[ -n "$LOW_COVERAGE" ]]; then
    echo "  Módulos con cobertura < 70%:"
    echo "$LOW_COVERAGE"
    echo ""
    echo "  Reasignar:"
    echo "    infrastructure-agent → tests en tests/infrastructure/"
    echo "    application-agent    → tests en tests/application/"
    echo "    domain-agent         → tests en tests/domain/"
  fi

  # Salida 2 → bloquea el cierre del turno del agente
  exit 2
fi

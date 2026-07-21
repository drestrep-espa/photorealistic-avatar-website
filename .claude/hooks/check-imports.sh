#!/usr/bin/env bash
# ============================================================
# check-imports.sh — PostToolUse hook
# Se dispara tras cada Edit / Write / MultiEdit.
# Verifica las cuatro reglas de dependencia de la arquitectura
# hexagonal del proyecto. Devuelve código de salida 2 si hay
# violaciones, bloqueando el turno del agente.
# ============================================================

set -euo pipefail

# ── Rutas base ──────────────────────────────────────────────
# Detecta las carpetas de cada capa de forma dinámica para no
# depender de rutas hardcodeadas (funciona en cualquier módulo).
DOMAIN_DIRS=$(find . -type d -name "domain" \
  | grep -v ".venv" | grep -v "__pycache__" | grep -v ".git" \
  | tr '\n' ' ' || true)

APPLICATION_DIRS=$(find . -type d -name "application" \
  | grep -v ".venv" | grep -v "__pycache__" | grep -v ".git" \
  | tr '\n' ' ' || true)

INFRASTRUCTURE_DIRS=$(find . -type d -name "infrastructure" \
  | grep -v ".venv" | grep -v "__pycache__" | grep -v ".git" \
  | tr '\n' ' ' || true)

HANDLER_DIRS=$(find . \( -type d -name "handler" -o -type d -name "endpoints" \) \
  | grep -v ".venv" | grep -v "__pycache__" | grep -v ".git" \
  | tr '\n' ' ' || true)

# Si no se encuentran capas, no hay nada que verificar
if [[ -z "$DOMAIN_DIRS" && -z "$APPLICATION_DIRS" ]]; then
  exit 0
fi

VIOLATIONS=0
REPORT=""

# ── Regla 1: domain/ no importa de otras capas ni de libs externas ──
if [[ -n "$DOMAIN_DIRS" ]]; then
  # Imports cruzados entre capas
  # Nota: "handler" se busca como módulo (precedido por "." o inicio de ruta)
  # para evitar falsos positivos con identificadores como "logging_handler".
  RESULT=$(grep -rn \
    "from.*application\|import.*application\|from.*infrastructure\|import.*infrastructure\|from.*endpoints\|import.*endpoints\|from handler\|from.*\.handler\b\|import handler\b\|import.*\.handler\b" \
    $DOMAIN_DIRS --include="*.py" \
    | grep -v "__pycache__" || true)

  if [[ -n "$RESULT" ]]; then
    VIOLATIONS=$((VIOLATIONS + 1))
    REPORT+="\nVIOLACIÓN — Regla 1: domain/ importa de otra capa\n"
    REPORT+="  El dominio es puro: no puede importar de application/, infrastructure/ ni endpoints/.\n"
    REPORT+="  Reasignar a: domain-agent\n"
    REPORT+="$RESULT\n"
  fi

  # Librerías de infraestructura en domain/
  RESULT=$(grep -rn \
    "import sqlalchemy\|from sqlalchemy\|import boto3\|from boto3\|import fastapi\|from fastapi\|import requests\|import httpx\|import celery\|import redis" \
    $DOMAIN_DIRS --include="*.py" \
    | grep -v "__pycache__" || true)

  if [[ -n "$RESULT" ]]; then
    VIOLATIONS=$((VIOLATIONS + 1))
    REPORT+="\nVIOLACIÓN — Regla 1b: domain/ importa librería de infraestructura\n"
    REPORT+="  El dominio no conoce boto3, sqlalchemy, fastapi ni ninguna librería externa.\n"
    REPORT+="  Reasignar a: domain-agent\n"
    REPORT+="$RESULT\n"
  fi
fi

# ── Regla 2: application/ no importa clases concretas de infrastructure/ ──
if [[ -n "$APPLICATION_DIRS" ]]; then
  RESULT=$(grep -rn \
    "from.*infrastructure\|import.*infrastructure" \
    $APPLICATION_DIRS --include="*.py" \
    | grep -v "__pycache__" || true)

  if [[ -n "$RESULT" ]]; then
    VIOLATIONS=$((VIOLATIONS + 1))
    REPORT+="\nVIOLACIÓN — Regla 2: application/ importa de infrastructure/\n"
    REPORT+="  Los casos de uso reciben interfaces (ABC de domain/), nunca adaptadores concretos.\n"
    REPORT+="  Reasignar a: application-agent\n"
    REPORT+="$RESULT\n"
  fi
fi

# ── Regla 3: infrastructure/ no importa de application/ ──
if [[ -n "$INFRASTRUCTURE_DIRS" ]]; then
  RESULT=$(grep -rn \
    "from.*application\|import.*application" \
    $INFRASTRUCTURE_DIRS --include="*.py" \
    | grep -v "__pycache__" || true)

  if [[ -n "$RESULT" ]]; then
    VIOLATIONS=$((VIOLATIONS + 1))
    REPORT+="\nVIOLACIÓN — Regla 3: infrastructure/ importa de application/\n"
    REPORT+="  Los adaptadores implementan puertos de domain/, no orquestan casos de uso.\n"
    REPORT+="  Reasignar a: infrastructure-agent\n"
    REPORT+="$RESULT\n"
  fi
fi

# ── Regla 4: handler/endpoints no importa entidades ni puertos de domain/ ──
# (las excepciones de dominio sí están permitidas en endpoints para el mapeo HTTP)
if [[ -n "$HANDLER_DIRS" ]]; then
  RESULT=$(grep -rn \
    "from.*domain.*import\|import.*domain" \
    $HANDLER_DIRS --include="*.py" \
    | grep -v "__pycache__" \
    | grep -v "Exception\|Error" || true)

  if [[ -n "$RESULT" ]]; then
    VIOLATIONS=$((VIOLATIONS + 1))
    REPORT+="\nVIOLACIÓN — Regla 4: endpoints/ importa entidades o puertos de domain/ directamente\n"
    REPORT+="  Los handlers solo pueden importar excepciones de domain/ (para mapeo HTTP).\n"
    REPORT+="  Cualquier uso de entidades o puertos indica lógica de negocio en el handler.\n"
    REPORT+="  Reasignar a: handler-agent\n"
    REPORT+="$RESULT\n"
  fi
fi

# ── Regla 5: tests de domain/ y application/ no usan MagicMock / @patch ──
TEST_DOMAIN_DIRS=$(find . -type d -path "*/tests*domain*" \
  | grep -v ".venv" | grep -v "__pycache__" | tr '\n' ' ')
TEST_APP_DIRS=$(find . -type d -path "*/tests*application*" \
  | grep -v ".venv" | grep -v "__pycache__" | tr '\n' ' ')

if [[ -n "$TEST_DOMAIN_DIRS" || -n "$TEST_APP_DIRS" ]]; then
  # -P usa Perl regex para que \b funcione de forma fiable
  RESULT=$(grep -Prn \
    "MagicMock|from unittest\.mock import Mock\b|@patch\b" \
    ${TEST_DOMAIN_DIRS:-} ${TEST_APP_DIRS:-} --include="*.py" \
    | grep -v "__pycache__" || true)

  if [[ -n "$RESULT" ]]; then
    VIOLATIONS=$((VIOLATIONS + 1))
    REPORT+="\nVIOLACIÓN — Regla 5: tests de domain/ o application/ usan mocks anónimos\n"
    REPORT+="  Usar Fake<Interfaz> que herede del puerto real (ver rules/testing.md).\n"
    REPORT+="  Reasignar a: domain-agent o application-agent según el fichero afectado.\n"
    REPORT+="$RESULT\n"
  fi
fi

# ── Resultado ────────────────────────────────────────────────
if [[ $VIOLATIONS -eq 0 ]]; then
  echo "✓ check-imports: todas las fronteras de capa correctas"
  exit 0
else
  echo "✗ check-imports: $VIOLATIONS violación(es) de frontera detectada(s)"
  echo -e "$REPORT"
  # Código de salida 2 → bloquea el turno del agente (Claude Code lo interpreta
  # como "acción rechazada por el sistema" y reporta el output al modelo).
  exit 2
fi

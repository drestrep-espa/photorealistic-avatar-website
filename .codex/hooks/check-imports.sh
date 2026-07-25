#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
ROOT="$(cd "$ROOT" && pwd)"
while [[ "$ROOT" != "/" && ! -d "$ROOT/.codex" ]]; do
  ROOT="$(dirname "$ROOT")"
done

if [[ ! -d "$ROOT/.codex" ]]; then
  echo "check-imports: no .codex root found"
  exit 0
fi

cd "$ROOT"

find_layer_dirs() {
  find . -type d "$@" \
    -not -path "*/.venv/*" \
    -not -path "*/venv/*" \
    -not -path "*/env/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.git/*" \
    -not -path "*/.claude/*" \
    -not -path "*/.codex/*" \
    -not -path "*/.agents/*"
}

mapfile -t DOMAIN_DIRS < <(find_layer_dirs -name "domain")
mapfile -t APPLICATION_DIRS < <(find_layer_dirs -name "application")
mapfile -t INFRASTRUCTURE_DIRS < <(find_layer_dirs -name "infrastructure")
mapfile -t HANDLER_DIRS < <(find_layer_dirs \( -name "handler" -o -name "endpoints" \))
mapfile -t TEST_DOMAIN_DIRS < <(find_layer_dirs -path "*/tests*domain*")
mapfile -t TEST_APP_DIRS < <(find_layer_dirs -path "*/tests*application*")

if [[ ${#DOMAIN_DIRS[@]} -eq 0 && ${#APPLICATION_DIRS[@]} -eq 0 ]]; then
  echo "check-imports: no Foqum layers found"
  exit 0
fi

VIOLATIONS=0
REPORT=""

append_violation() {
  local title="$1"
  local detail="$2"
  local result="$3"
  VIOLATIONS=$((VIOLATIONS + 1))
  REPORT+=$'\n'"VIOLATION - ${title}"$'\n'
  REPORT+="  ${detail}"$'\n'
  REPORT+="${result}"$'\n'
}

run_grep() {
  local pattern="$1"
  shift
  if [[ "$#" -eq 0 ]]; then
    return 0
  fi
  grep -RInE "$pattern" "$@" --include="*.py" 2>/dev/null | grep -v "__pycache__" || true
}

if [[ ${#DOMAIN_DIRS[@]} -gt 0 ]]; then
  RESULT=$(run_grep "from .*application|import .*application|from .*infrastructure|import .*infrastructure|from .*endpoints|import .*endpoints|from .*handler\\b|import .*handler\\b" "${DOMAIN_DIRS[@]}")
  if [[ -n "$RESULT" ]]; then
    append_violation \
      "Rule 1: domain imports another layer" \
      "Domain is pure and cannot import application, infrastructure, endpoints, or handler. Reassign to domain-agent." \
      "$RESULT"
  fi

  RESULT=$(run_grep "import sqlalchemy|from sqlalchemy|import boto3|from boto3|import fastapi|from fastapi|import requests|import httpx|import celery|import redis" "${DOMAIN_DIRS[@]}")
  if [[ -n "$RESULT" ]]; then
    append_violation \
      "Rule 1b: domain imports infrastructure/framework libraries" \
      "Domain cannot know boto3, SQLAlchemy, FastAPI, HTTP clients, Redis, or Celery. Reassign to domain-agent." \
      "$RESULT"
  fi
fi

if [[ ${#APPLICATION_DIRS[@]} -gt 0 ]]; then
  RESULT=$(run_grep "from .*infrastructure|import .*infrastructure" "${APPLICATION_DIRS[@]}")
  if [[ -n "$RESULT" ]]; then
    append_violation \
      "Rule 2: application imports infrastructure" \
      "Use cases receive domain interfaces, never concrete adapters. Reassign to application-agent." \
      "$RESULT"
  fi
fi

if [[ ${#INFRASTRUCTURE_DIRS[@]} -gt 0 ]]; then
  RESULT=$(run_grep "from .*application|import .*application" "${INFRASTRUCTURE_DIRS[@]}")
  if [[ -n "$RESULT" ]]; then
    append_violation \
      "Rule 3: infrastructure imports application" \
      "Adapters implement domain ports and do not orchestrate use cases. Reassign to infrastructure-agent." \
      "$RESULT"
  fi
fi

if [[ ${#HANDLER_DIRS[@]} -gt 0 ]]; then
  RESULT=$(run_grep "from .*domain.*import|import .*domain" "${HANDLER_DIRS[@]}" | grep -vE "Exception|Error" || true)
  if [[ -n "$RESULT" ]]; then
    append_violation \
      "Rule 4: handler/endpoints imports domain entities or ports" \
      "Handlers may import domain exceptions for HTTP mapping, but not entities or ports. Reassign to handler-agent." \
      "$RESULT"
  fi
fi

TEST_DIRS=("${TEST_DOMAIN_DIRS[@]}" "${TEST_APP_DIRS[@]}")
if [[ ${#TEST_DIRS[@]} -gt 0 ]]; then
  RESULT=$(run_grep "MagicMock|from unittest\\.mock import Mock\\b|@patch\\b" "${TEST_DIRS[@]}")
  if [[ -n "$RESULT" ]]; then
    append_violation \
      "Rule 5: domain/application tests use anonymous mocks" \
      "Use Fake<Port> classes that inherit the real domain port. Reassign to domain-agent or application-agent." \
      "$RESULT"
  fi
fi

if [[ "$VIOLATIONS" -eq 0 ]]; then
  echo "check-imports: all layer boundaries pass"
  exit 0
fi

echo "check-imports: ${VIOLATIONS} boundary violation(s) found"
printf "%s\n" "$REPORT"
exit 2

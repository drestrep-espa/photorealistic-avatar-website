---
id: "0003"
titulo: Umbral de cobertura mínimo del 80% con gate de regresión
estado: Aceptada
---

# ADR 0003 — Coverage Floor 80%

## Contexto

Sin un umbral mínimo, la cobertura tiende a degradarse incrementalmente
a medida que se añaden features sin tests. Un umbral demasiado alto
(> 90%) penaliza código de infraestructura legítimamente difícil de
cubrir (Bedrock con soporte parcial en moto).

## Decision

Umbral absoluto: **80%** (`fail_under = 80` en `pyproject.toml`).

Además del umbral absoluto, el hook `coverage-gate.sh` implementa un
**gate de regresión**: si la cobertura baja más de 1 punto respecto al
baseline del último commit, el turno del agente queda bloqueado aunque
esté por encima del 80%.

## Alternativas consideradas

1. **Sin umbral** — rechazado: la cobertura degrada sin presión automática.
2. **90%** — rechazado: los adaptadores AWS con soporte parcial en moto
   requieren `patch` que no cubre todas las ramas; 90% sería inalcanzable
   sin tests artificiales.
3. **Solo umbral absoluto** — rechazado: permite bajar de 87% a 81%
   en un solo PR sin alarma si el umbral es 80%.

## Consecuencias

- Cada turno de agente que escribe código Python y baja la cobertura
  queda bloqueado con salida 2 antes de terminar.
- Los módulos con cobertura < 70% se reportan con las líneas exactas
  sin cubrir para facilitar la reasignación.
- El hook solo se ejecuta cuando hay cambios Python (guarda de git status),
  evitando correr la suite completa en turnos de solo lectura.
- Configurado en `pyproject.toml` → cualquier cambio al umbral queda en
  el historial de git y requiere revisión (ver `CODEOWNERS`).

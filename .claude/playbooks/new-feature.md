---
name: nueva-feature
tipo: playbook
---

# Playbook — Nueva Feature

## Objetivo

Implementar una feature nueva end-to-end siguiendo el orden de delegación
TDD: domain → application + infrastructure (paralelo) → handler → PR.

## Cuando Usar

Cuando la tarea cree funcionalidad que no existe: nuevo puerto, nuevo caso
de uso, nuevo endpoint o nueva integración con un servicio externo.

## Pasos

### 1. Definir el contrato en CLAUDE.md

Antes de delegar, el orquestador define en el contexto:
- Qué entidad o puerto nuevo se necesita.
- Qué caso de uso lo orquesta.
- Qué endpoint lo expone.
- Qué tecnología implementa el puerto.

### 2. Delegar a domain-agent

Tarea: crear la entidad, el puerto ABC y las excepciones de negocio.

Proporcionar: nombre del concepto, campos, reglas de validación, métodos
del puerto con sus firmas.

Esperar el reporte de domain-agent con: puertos nuevos (firma exacta),
Fakes generados, Object Mothers generados.

### 3. Delegar en paralelo a application-agent e infrastructure-agent

**application-agent**: crear el caso de uso que orquesta el puerto nuevo.
Proporcionar: firma exacta del puerto (del reporte de domain-agent).

**infrastructure-agent**: crear el adaptador que implementa el puerto.
Proporcionar: firma del puerto, tecnología a usar, parámetros de config.

### 4. Delegar a handler-agent

Tarea: crear el endpoint FastAPI y el wiring.
Proporcionar: firma del caso de uso (de application-agent), nombre del
adaptador e instrucciones de instanciación (de infrastructure-agent).

### 5. Ejecutar reviewer-agent

```
/reviewer-agent
```

No abrir el PR hasta que el revisor dé veredicto LISTO PARA PR.

## Verificación

- Todos los tests pasan (`/run-layer-tests all` desde reviewer-agent).
- Cobertura ≥ 80% y no ha bajado respecto al baseline.
- `check-import-boundaries` sin violaciones.
- El endpoint responde correctamente en tests e2e.

## Controles PSI-12

- Los adaptadores nuevos leen credenciales desde variables de entorno.
- Los tests de infraestructura usan credenciales ficticias (`aws_credentials`).
- No abrir PR con el checklist §7 incompleto.

## Riesgos

- domain-agent define un puerto con firma incorrecta → los otros dos agentes
  fallan. Solución: volver a domain-agent con la corrección antes de continuar.
- infrastructure-agent necesita un método que no está en el puerto →
  señal de parada: el método lo añade domain-agent, no infrastructure-agent.

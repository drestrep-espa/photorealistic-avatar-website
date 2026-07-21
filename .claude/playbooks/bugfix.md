---
name: bugfix
tipo: playbook
---

# Playbook — Bugfix

## Objetivo

Corregir un defecto identificado siguiendo el ciclo TDD: test que reproduce
el bug → fix mínimo → verificación.

## Cuando Usar

Cuando hay un comportamiento incorrecto documentado (error de producción,
fallo de test, reporte de usuario). No usar para mejoras o refactors.

## Pasos

### 1. Identificar la capa afectada

Leer el stack trace o la descripción del bug y determinar en qué capa vive:

| Síntoma | Capa probable |
|---|---|
| Regla de negocio incorrecta, entidad con estado inválido | `domain/` |
| Caso de uso no orquesta correctamente | `application/` |
| Fallo al leer/escribir en AWS, BD, HTTP externo | `infrastructure/` |
| Error HTTP incorrecto, wiring roto, schema inválido | `endpoints/` |

### 2. Escribir el test que reproduce el bug (Red)

**Antes de tocar el código de producción**, escribir el test que falla
exactamente por el bug reportado. Esto es la Red del ciclo TDD.

Delegar al agente de la capa identificada con la instrucción:
"Escribe el test que reproduce este bug antes de arreglarlo."

### 3. Aplicar el fix mínimo (Green)

Con el test fallando, implementar el cambio mínimo que lo hace pasar.
No refactorizar en este paso — solo hacer pasar el test.

### 4. Verificar que no se rompió nada (Refactor + Suite)

```bash
/run-layer-tests <capa afectada>
```

Si el bug tocaba varias capas, correr las capas afectadas en orden:
domain → application → infrastructure → handler.

### 5. Ejecutar reviewer-agent

```
/reviewer-agent
```

## Verificación

- El test nuevo pasa y reproduce exactamente el bug original.
- Ningún test previo que pasaba ha dejado de pasar.
- Cobertura no ha bajado.

## Controles PSI-12

- No relajar validaciones de seguridad para hacer pasar el test.
- Si el bug involucra datos de usuario o credenciales, verificar que el
  fix no expone esa información en logs o respuestas HTTP.

## Riesgos

- Fix que hace pasar el test pero no resuelve el caso real → revisar que
  el test replica las condiciones exactas del bug, no una aproximación.
- Fix en `infrastructure/` que introduce lógica de negocio → señal de
  parada; la lógica debe ir a `domain/` o `application/`.

---
name: api-change
tipo: playbook
---

# Playbook — Cambio de API

## Objetivo

Modificar un endpoint existente (nueva ruta, cambio de schema, nuevo
parámetro, cambio de código de respuesta) manteniendo la coherencia entre
capas y sin romper contratos existentes.

## Cuando Usar

Cuando se añade, modifica o elimina un endpoint FastAPI, un schema Pydantic
de entrada/salida, o el mapeo de excepciones de dominio a HTTP.

## Pasos

### 1. Evaluar el impacto en capas

Determinar si el cambio de API implica:
- **Solo handler**: cambio de schema o código HTTP → delegar a `handler-agent`.
- **Application + handler**: nueva lógica de orquestación → delegar en orden.
- **Domain + application + handler**: nuevo concepto de negocio → seguir
  el playbook `new-feature.md` en su lugar.

### 2. Actualizar el contrato de dominio si aplica

Si el cambio requiere un puerto nuevo o modificado: primero `domain-agent`.
Si el caso de uso cambia su firma o comportamiento: después `application-agent`.

### 3. Delegar a handler-agent

Proporcionar:
- Ruta HTTP exacta (método + path).
- Schema de request nuevo o modificado.
- Schema de response nuevo o modificado.
- Mapeo de excepciones de dominio → HTTP status si cambia.

### 4. Verificar los tests e2e

```bash
/run-layer-tests handler
```

Los tests e2e deben cubrir:
- El camino feliz con la nueva firma.
- Los errores principales mapeados a HTTP.
- Que los endpoints anteriores siguen funcionando (no regresión).

### 5. Ejecutar reviewer-agent

```
/reviewer-agent
```

## Verificación

- Los tests e2e del endpoint modificado pasan.
- Ningún endpoint existente ha dejado de funcionar.
- El schema de request/response nuevo es Pydantic separado de las entidades.
- Los errores de dominio tienen mapeo explícito a HTTP status.

## Controles PSI-12

- Verificar que el endpoint nuevo no expone datos sensibles en la respuesta
  (credenciales, IDs internos de infraestructura, stack traces).
- Si el endpoint recibe datos de usuario, validar con Pydantic antes de
  pasarlos al caso de uso. No confiar en el request sin validación.
- Comprobar que la autenticación/autorización aplica al endpoint nuevo
  (si los endpoints existentes tienen `Depends(auth)`, el nuevo también).

## Riesgos

- Schema de respuesta que expone campos internos de la entidad de dominio →
  usar siempre un schema Pydantic de response separado, no `entity.model_dump()`.
- Cambio de código HTTP que rompe clientes existentes → documentar en el
  PR si el cambio es breaking change.

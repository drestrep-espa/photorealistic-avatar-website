---
name: foqum-architecture
description: "Carga la guía corporativa Foqum para proyectos Python con Arquitectura Hexagonal, DDD, TDD, fronteras de capas, dobles de prueba, Object Mothers y convenciones de nombrado. Úsala antes de implementar o revisar cambios que toquen domain, application, infrastructure, endpoints, handler, tests, fakes, mothers o adaptadores."
---

# Arquitectura Foqum

Usa esta skill para alinear el trabajo con la arquitectura Foqum antes de
programar o revisar.

Lee solo los ficheros de referencia relevantes para la tarea actual:

- `references/ddd-layers.md`: responsabilidades de capa y dirección de
  dependencias.
- `references/testing.md`: TDD, pirámide de tests, Fakes, Object Mothers y
  fixtures.
- `references/naming.md`: convenciones corporativas de nombrado.

Flujo:

1. Identifica la capa o capas afectadas por la petición.
2. Lee los ficheros de referencia correspondientes.
3. Revisa el módulo vecino más parecido y replica su patrón local.
4. Mantén el cambio en la capa más pequeña que sea dueña del comportamiento.
5. Verifica con el comando `$run-layer-tests` correspondiente y, antes del PR,
   `$pr-checklist`.

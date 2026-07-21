---
id: "0001"
titulo: Arquitectura hexagonal como estructura de capas
estado: Aceptada
---

# ADR 0001 — Arquitectura Hexagonal

## Contexto

`doc_compare_proapsa_v2` integra múltiples servicios externos intercambiables:
un índice RAG para normativa, un LLM para extracción/redacción, y un
extractor de texto/tablas de PDF. El sistema debe poder cambiar de
proveedor (de motor RAG, de LLM, de municipio, de normativa) sin que la
lógica de negocio — qué es un hallazgo, qué reglas se comparan, qué
evidencia se exige — quede acoplada a ningún SDK ni a Boadilla del Monte
en particular.

## Decision

Adoptar arquitectura hexagonal (Ports and Adapters) con cuatro capas:

```
endpoints → application → domain ← infrastructure
```

- `domain/`: entidades del dominio (`ProjectState`, `Finding`, `CheckResult`,
  reglas estructuradas...), puertos (`NormativeRetriever`, `LlmService`,
  `PdfTextExtractor`...) y excepciones de negocio. Sin dependencias externas.
- `application/`: las tools del orquestador (`analyze_project`,
  `retrieve_normative`, `select_and_run_checks`, `enrich_with_evidence`,
  `generate_review_output`) como casos de uso que orquestan puertos.
- `infrastructure/`: adaptadores concretos (motor RAG, cliente LLM,
  extractor de PDF, repositorio de reglas).
- `endpoints/`: wiring del orquestador, mapeo de excepciones de dominio.

## Alternativas consideradas

1. **Agente libre que lee el PDF y opina** — rechazado: sin tools con
   responsabilidad acotada no hay trazabilidad ni evidencia verificable
   por hallazgo, que es un requisito explícito del proyecto.
2. **Sin capas explícitas** — rechazado: acoplar la lógica de negocio a un
   proveedor de RAG/LLM concreto impide cambiarlo o añadir municipios sin
   reescribir los checks.

## Consecuencias

- Los tests de `domain/` y `application/` corren en milisegundos sin red,
  sin llamar al LLM real ni al índice RAG real.
- Cambiar de proveedor (RAG, LLM, extractor de PDF) solo afecta a
  `infrastructure/`; añadir un municipio nuevo solo añade normativa y
  reglas, no toca el dominio.
- Los agentes de IA tienen alcance acotado por capa — reducen el riesgo
  de cambios accidentales cross-layer.
- Los hooks `check-imports.sh` verifican las fronteras automáticamente.

## Delegación de subagentes

Antes de implementar cualquier cambio que toque `domain/`, `application/`,
`infrastructure/` o `endpoints/`: lee este fichero + el módulo vecino más
parecido (regla de oro nº1: antes de escribir, lee y copia el patrón).

Define el contrato (qué entidad / puerto / caso de uso / adaptador / endpoint)
y delega según esta tabla:

| Si la tarea toca... | Subagente |
|---|---|
| Entidades, value objects, puertos ABC, excepciones de negocio | `domain-agent` |
| Casos de uso que orquestan puertos existentes | `application-agent` |
| Adaptadores concretos (SQL, Bedrock, S3, Textract, moto...) | `infrastructure-agent` |
| FastAPI handlers, esquemas Pydantic, wiring, mapeo de errores | `handler-agent` |

El contrato definido aquí debe pasarse explícitamente en el prompt de cada
subagente: los subagentes no se ven entre sí, solo reportan a esta sesión.

Orden de delegación TDD:
1. `domain-agent` primero (define el puerto → escribe test → implementa)
2. `application-agent` + `infrastructure-agent` en paralelo (ambos dependen
   del puerto ya definido, no entre sí)
3. `handler-agent` al final (ensambla lo anterior)
4. Ejecutar `/pr-checklist` antes de cerrar la tarea

## Fuera de alcance — nunca tocar sin confirmación explícita

- Ficheros autogenerados por migraciones de Alembic
- `.env` y cualquier fichero de credenciales
- Configuración de infraestructura AWS (Terraform, CDK, CloudFormation)
- `shared/` — módulo compartido entre aplicaciones; cambios tienen efecto
  transversal

## Regla de oro nº 2

El código sin test no está terminado. Por cada fichero nuevo o modificado
en `<capa>/`, debe existir o actualizarse `tests/<capa misma ruta>/`.

## Proyecto

`doc_compare_proapsa_v2` es una herramienta de pre-revisión automática de
proyectos básicos de arquitectura/construcción frente a normativa
urbanística municipal (PGOU, ordenanzas, planes parciales). No certifica
cumplimiento legal: detecta documentación faltante, incoherencias internas,
normativa mal citada, referencias arrastradas de otro proyecto, parámetros
urbanísticos no justificados, posibles incumplimientos y puntos que
requieren revisión por un técnico competente.

Principio de diseño: RAG para recuperar normativa + reglas estructuradas
para comparar valores + un orquestador con tools que decide qué ejecutar +
LLM para extraer/interpretar/redactar + código determinista para cálculos y
comparaciones numéricas. Nunca un agente libre que lea el PDF entero y dé
una opinión general — cada tool tiene una responsabilidad acotada y toda
conclusión relevante lleva evidencia (página, fragmento, documento).

El orquestador ejecuta, en este orden, las tools definidas como casos de
uso en `application/`:

1. `analyze_project` — lee el PDF del proyecto y construye el
   `project_state` (mapa del documento, perfil, parámetros urbanísticos,
   planos, normativa citada). Solo extrae hechos, nunca concluye. Puede
   procesar el PDF por chunks de ~20 páginas, pero cada chunk solo
   actualiza el estado global — las decisiones se toman después, con el
   estado completo.
2. `retrieve_normative` — recupera normativa aplicable vía RAG (semántica +
   metadatos) usando el perfil del proyecto. No compara valores, solo
   recupera y sugiere checks.
3. `select_and_run_checks` — selecciona y ejecuta checks documentales, de
   coherencia, urbanísticos, de planos y CTE básicos según el perfil del
   proyecto. Las comparaciones numéricas son código determinista, nunca
   las decide el LLM.
4. `enrich_with_evidence` — añade evidencia trazable (documento, página,
   fragmento, tipo de evidencia, confianza) a cada resultado de check. Sin
   evidencia suficiente, el check baja de confianza o pasa a "requiere
   revisión" — nunca se inventa.
5. `generate_review_output` — genera el JSON final, el informe legible, la
   tabla de cumplimiento urbanístico y los hallazgos con categoría,
   gravedad, evidencia y propuesta de subsanación (nunca corrige el
   documento original, solo propone).

`normative_indexer` es un proceso previo, no parte del flujo de cada
revisión: indexa normativa en RAG con metadatos (municipio, documento,
capítulo, artículo, página, vigencia) y prepara/asocia reglas estructuradas
comparables. No decide si el proyecto cumple.

Estados de hallazgo — nunca afirmaciones absolutas de legalidad ("es
legal" / "es ilegal"): cumple según la información encontrada, no cumple,
no se ha localizado justificación, posible incoherencia, posible
incumplimiento, requiere revisión técnica, pendiente de validación humana.

Caso de prueba de la primera iteración: proyecto básico de Boadilla del
Monte + PGOU/normas urbanísticas de Boadilla. La arquitectura no debe
quedar acoplada a Boadilla ni a ningún municipio: cualquier dato específico
de municipio vive en normativa indexada o en reglas estructuradas, nunca
hardcodeado en `domain/` ni `application/`.

Estructura: `src/{domain,application,infrastructure,endpoints}/`

## Puntos de entrada

- `src/endpoints/` — punto de entrada del orquestador; instancia los
  adaptadores concretos (RAG, LLM, extracción de PDF) e invoca en orden las
  tools de `application/` descritas arriba.

## Tests

- Ubicación: `tests/` con ruta espejo a `src/`
- Fakes: `tests/fakes/` | Object Mothers: `tests/mothers/`
- Correr todos: `.venv/bin/pytest tests/ -v` (`.venv/Scripts/pytest` en Windows)
- Correr por capa: `.venv/bin/pytest tests/<capa>/ -v`

## Hooks activos (automáticos)

Dos hooks se ejecutan automáticamente — no es necesario invocarlos:

- **Cada Edit / Write / MultiEdit** → `.claude/hooks/check-imports.sh`
  Sale con código 2 si algún archivo viola las fronteras de capas DDD.
- **Cada Stop** (si hay cambios Python) → `.claude/hooks/coverage-gate.sh`
  Sale con código 2 si la cobertura cae por debajo del 80% o baja respecto
  al baseline del último commit.

Si un turno termina bloqueado sin explicación visible, es un hook que
detectó una violación. Corregir la causa antes de continuar.

## Reglas detalladas

- `.claude/rules/ddd-layers.md` — qué puede importar cada capa
- `.claude/rules/naming.md` — prefijos de adaptadores, nombres de puertos y Fakes
- `.claude/rules/testing.md` — TDD, Fakes vs MagicMock, Object Mothers

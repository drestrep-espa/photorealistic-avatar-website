# Guía Foqum para Codex

## Acuerdo de trabajo

Antes de implementar cualquier cambio que toque `domain/`, `application/`,
`infrastructure/`, `endpoints/` o `handler/`, lee este fichero y el módulo
vecino más parecido. Primero copia el patrón local; después escribe el cambio
más pequeño que resuelva la tarea.

Define el contrato antes de editar:

| Si la tarea toca... | Rol Codex |
|---|---|
| Entidades, value objects, puertos ABC, excepciones de negocio | `domain-agent` |
| Casos de uso que orquestan puertos existentes | `application-agent` |
| Adaptadores concretos como SQL, Bedrock, S3, Textract, moto | `infrastructure-agent` |
| Handlers FastAPI, esquemas Pydantic, wiring, mapeo de errores | `handler-agent` |

Codex solo lanza subagentes cuando el usuario lo pide explícitamente. Si el
usuario pide delegación, trabajo en paralelo o un agente por capa, usa los
agentes personalizados de `.codex/agents/`. En cualquier otro caso, aplica las
instrucciones del rol correspondiente en el hilo principal.

## Orden TDD

1. `domain-agent` primero: define el puerto o la entidad, escribe el test que
   falla y después implementa.
2. `application-agent` e `infrastructure-agent` pueden trabajar cuando el
   puerto de dominio ya existe. Dependen del puerto, no entre sí.
3. `handler-agent` va al final y ensambla el sistema.
4. Ejecuta `$pr-checklist` antes de marcar como lista una tarea preparada para PR.

## Fuera de alcance sin confirmación explícita

- Ficheros de migraciones Alembic generados por herramientas.
- `.env` y cualquier fichero de credenciales.
- Configuración de infraestructura AWS: Terraform, CDK, CloudFormation.
- `shared/`, porque los cambios ahí tienen impacto transversal.

## Reglas de arquitectura

La dirección de dependencias es:

```text
handler/endpoints -> application -> domain <- infrastructure
```

- `domain/` es código de dominio Python puro. No debe importar FastAPI,
  SQLAlchemy, boto3, requests, httpx, Redis, Celery ni ninguna otra dependencia
  de infraestructura o framework.
- `application/` recibe puertos de dominio como interfaces. No debe importar
  clases concretas de infraestructura.
- `infrastructure/` implementa puertos de dominio. No debe orquestar casos de
  uso de aplicación ni contener decisiones de negocio.
- `handler/` y `endpoints/` exponen entrada/salida, instancian adaptadores,
  llaman a casos de uso y mapean excepciones de dominio a respuestas HTTP. No
  contienen lógica de negocio.

## Reglas de testing

El código sin tests no está terminado. Por cada fichero nuevo o modificado bajo
una capa, añade o actualiza los tests espejo en `tests/<misma ruta de capa>/`.

Usa TDD:

1. Red: escribe primero el test que falla.
2. Green: implementa el mínimo código que lo hace pasar.
3. Refactor: limpia sin cambiar comportamiento.

Usa clases `Fake<Port>` que hereden de puertos reales de dominio en tests de
`domain/` y `application/`. No uses `MagicMock`, `Mock` anónimo ni `@patch` en
esas capas. Los Object Mothers viven bajo tests y crean objetos de dominio
válidos por defecto.

Antes de ejecutar pytest, linters o herramientas Python, usa `$python-sandbox`
si el entorno virtual no se ha verificado en esta sesión.

## Skills

- `$foqum-architecture`: carga convenciones de DDD, testing y nombrado.
- `$python-sandbox`: prepara o verifica el entorno virtual Python.
- `$run-layer-tests`: ejecuta tests de una sola capa.
- `$scaffold-fake`: crea un `Fake<Port>` para un puerto de dominio.
- `$scaffold-object-mother`: crea un Object Mother para una entidad de dominio.
- `$setup-aws-mock`: prepara guía moto/localstack para tests de adaptadores AWS.
- `$check-import-boundaries`: audita la dirección de dependencias entre capas.
- `$coverage-gate`: ejecuta el gate de cobertura.
- `$pr-checklist`: completa el flujo de verificación previo al PR.

## Estilo

Prefiere cambios pequeños, explícitos y locales. Usa nombres, estructura de
directorios, estilo Pydantic/dataclass, fixtures y adaptadores existentes como
fuente de verdad. No añadas abstracciones ni dependencias de producción salvo
que la tarea las necesite.

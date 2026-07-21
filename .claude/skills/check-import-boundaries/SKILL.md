---
name: check-import-boundaries
description: Verifica las cuatro reglas de dependencia entre capas de la arquitectura hexagonal del proyecto usando búsquedas de imports. Detecta violaciones (domain importando infrastructure, application importando clases concretas, etc.) y produce un informe listo para incluir en el checklist del reviewer-agent. Úsala cuando reviewer-agent ejecute el punto 3 del checklist, o cuando el usuario pida "verifica las dependencias entre capas", "comprueba que no hay imports cruzados", "audita la dirección de dependencias".
triggers:
  - "verifica las dependencias entre capas"
  - "comprueba que no hay imports cruzados"
  - "audita la dirección de dependencias"
  - "check-import-boundaries"
  - "imports entre capas"
---

# Check Import Boundaries

Verifica que las dependencias entre capas siguen la regla de la arquitectura
hexagonal del proyecto:

```
handler → application → domain ← infrastructure
```

Esta skill produce un informe estructurado de violaciones listo para
incluir en el informe del `reviewer-agent`.

## 1. Detectar la estructura de carpetas del proyecto

Antes de buscar, identifica los nombres reales de las carpetas de cada capa
en el proyecto (pueden variar):

```bash
# Busca las carpetas de cada capa
find . -type d -name "domain" | grep -v ".venv" | grep -v "__pycache__"
find . -type d -name "application" | grep -v ".venv" | grep -v "__pycache__"
find . -type d -name "infrastructure" | grep -v ".venv" | grep -v "__pycache__"
find . -type d -name "handler" -o -type d -name "endpoints" | grep -v ".venv"
```

En Windows usa `glob` para lo mismo. Registra las rutas encontradas —
las necesitarás para acotar las búsquedas de imports.

## 2. Ejecutar las cuatro comprobaciones

### Regla 1 — El dominio no importa nada de las otras capas

```bash
grep -rn \
  "from.*application\|import.*application\|from.*infrastructure\|import.*infrastructure\|from.*handler\|import.*handler\|from.*endpoints\|import.*endpoints" \
  **/domain/ \
  --include="*.py" \
  | grep -v "__pycache__"
```

**Cualquier resultado es una violación.** El dominio solo puede importar
de sí mismo y de la stdlib de Python.

### Regla 2 — Application no importa clases concretas de infrastructure

```bash
grep -rn \
  "from.*infrastructure\|import.*infrastructure" \
  **/application/ \
  --include="*.py" \
  | grep -v "__pycache__"
```

`application/` solo debe importar interfaces (ABCs) de `domain/`.
Si importa algo de `infrastructure/`, es una violación directa.

### Regla 3 — Infrastructure no importa de application

```bash
grep -rn \
  "from.*application\|import.*application" \
  **/infrastructure/ \
  --include="*.py" \
  | grep -v "__pycache__"
```

`infrastructure/` implementa puertos de `domain/` pero no debe orquestar
casos de uso de `application/`.

### Regla 4 — Handler/endpoints no contiene lógica de negocio interna

Esta regla no se puede verificar solo con imports, pero sí con señales:

```bash
# Detecta imports de entidades de dominio usadas directamente en el handler
# (señal de que se está haciendo lógica que debería estar en application/)
grep -rn \
  "from.*domain.*import\|import.*domain" \
  **/handler/ **/endpoints/ \
  --include="*.py" \
  | grep -v "__pycache__" \
  | grep -v "Exception\|Error"  # Las excepciones de dominio sí pueden importarse en handler
```

Los únicos imports de `domain/` permitidos en `handler/` son excepciones
de negocio (para el mapeo a HTTPException). Si importa entidades o puertos
directamente, es señal de lógica de negocio en el handler.

## 3. Comprobaciones adicionales

### Librerías externas en domain/

```bash
grep -rn \
  "import sqlalchemy\|from sqlalchemy\|import boto3\|from boto3\|import requests\|import httpx\|import fastapi\|from fastapi\|import celery\|import redis" \
  **/domain/ \
  --include="*.py" \
  | grep -v "__pycache__"
```

### Mocks anónimos en tests de domain/ y application/

```bash
grep -rn \
  "MagicMock\|from unittest.mock import Mock\b\|@patch\b" \
  tests/**/domain/ tests/**/application/ \
  --include="*.py" \
  | grep -v "__pycache__"
```

Los tests de dominio y aplicación deben usar `Fake<Interfaz>`, no mocks
anónimos.

## 4. Interpretar los resultados

Para cada línea devuelta por grep:

- Extrae: archivo, número de línea, contenido del import.
- Clasifica la violación según qué regla rompe.
- Determina el agente al que reasignar:
  - Import externo en `domain/` → `domain-agent`
  - Import de `infrastructure/` en `application/` → `application-agent`
  - Import de `application/` en `infrastructure/` → `infrastructure-agent`
  - Lógica de negocio en `handler/` → `handler-agent`
  - Mock anónimo en tests de `domain/` → `domain-agent`
  - Mock anónimo en tests de `application/` → `application-agent`

## 5. Resultado

Si no hay violaciones:
```
Comprobación de fronteras de imports: PASA
Las cuatro reglas de dependencia se cumplen en todo el proyecto.
```

Si hay violaciones:
```
Comprobación de fronteras de imports: FALLA
<N> violaciones encontradas:

Violación 1 — Regla <N>: <descripción de la regla>
  Archivo: src/domain/user.py:12
  Import: from infrastructure.sql import SqlSession
  Reasignar a: domain-agent

Violación 2 — ...
```

Entrega el informe completo para que `reviewer-agent` lo incluya en el
punto 3 de su checklist.

## No Usar Cuando

En proyectos sin estructura de capas DDD. Esta skill produce el informe
estructurado — la automatización continua la realiza el hook `check-imports.sh`
(se dispara en cada Edit/Write automáticamente).

## Controles PSI-12

Verificar siempre que `infrastructure/` no expone secretos de entorno
directamente en los imports comprobados. La presencia de imports de `boto3`
o `sqlalchemy` en `domain/` es una señal de riesgo de fuga de credenciales.

## Referencias

- Reglas de capas: `.claude/rules/ddd-layers.md`
- Hook equivalente automático: `.claude/hooks/check-imports.sh`
- Agente que la invoca: `reviewer-agent`

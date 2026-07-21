---
name: pr-checklist
description: Ejecuta el checklist completo de la guía del proyecto antes de abrir un Pull Request. Corre run-layer-tests all, verifica imports entre capas, comprueba cobertura y revisa cada punto del checklist §7. Usar cuando la feature está terminada y antes de abrir el PR. No usar durante el desarrollo normal.
triggers:
  - "ejecuta el checklist"
  - "checklist de PR"
  - "pre-PR"
  - "antes de abrir el PR"
  - "revisa el PR"
---

# PR Checklist — guía del proyecto §7

Ejecuta los siguientes pasos en orden. Para cada punto indica PASA / FALLA
y el fichero afectado si falla.

## 1. Tests completos

```bash
.venv/Scripts/pytest tests/ -v
```

Si falla: identifica la capa (domain/application/infrastructure/endpoints) y
reporta al subagente correspondiente. No continuar hasta que la suite pase.

## 2. Cobertura

```bash
.venv/Scripts/pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

Si la cobertura bajó respecto al estado anterior en algún módulo, reportar
qué módulos y qué subagente debe añadir tests.

## 3. Verificación de imports entre capas

Detecta las carpetas de cada capa dinámicamente:

```bash
DOMAIN_DIRS=$(find . -type d -name "domain" | grep -v ".venv" | grep -v "__pycache__")
APPLICATION_DIRS=$(find . -type d -name "application" | grep -v ".venv" | grep -v "__pycache__")
```

Verifica cada regla:

```bash
# domain/ no puede importar de application/, infrastructure/, endpoints/
for dir in $DOMAIN_DIRS; do
  grep -rn "from.*application\|from.*infrastructure\|from.*endpoints" "$dir" \
    --include="*.py" | grep -v "__pycache__" \
    && echo "VIOLACIÓN en $dir" || echo "$dir OK"
done

# application/ no puede importar de infrastructure/ ni endpoints/
for dir in $APPLICATION_DIRS; do
  grep -rn "from.*infrastructure\|from.*endpoints" "$dir" \
    --include="*.py" | grep -v "__pycache__" \
    && echo "VIOLACIÓN en $dir" || echo "$dir OK"
done
```

Si hay violaciones: reportar fichero y línea exactos. Reasignar a
`domain-agent` o `application-agent` según qué capa viola.

## 4. Checklist de revisión manual

- [ ] El cambio está en la capa correcta (dominio sin SQL/HTTP/AWS; lógica
      de negocio fuera de endpoints/).
- [ ] Los casos de uso reciben interfaces (ABC), no implementaciones concretas.
- [ ] Herencia solo para contratos (ABC); comportamiento por composición.
- [ ] Se hizo el cambio más pequeño que resuelve el problema. Nada "por si acaso".
- [ ] Se siguió el patrón existente en ficheros vecinos (nombrado, estructura).
- [ ] Tests en la ruta espejo correcta con Object Mothers y Fakes.
- [ ] Nuevos adaptadores tienen prefijo de tecnología en el nombre.
- [ ] Nuevas excepciones heredan de Exception y están en domain/exceptions.py.
- [ ] No hay credenciales, tokens ni rutas personales hardcodeadas.

## 5. Lint y tipos

```bash
.venv/Scripts/ruff check . && .venv/Scripts/ruff format --check . && .venv/Scripts/mypy src/
```

Si falla: son correcciones mecánicas. Aplicar antes de continuar.

## No Usar Cuando

Durante el desarrollo normal de una feature. Solo ejecutar cuando la tarea
esté terminada y lista para revisión.

## Controles PSI-12

- El punto 4 incluye verificación explícita de ausencia de credenciales
  hardcodeadas antes de abrir el PR.
- No aprobar un PR donde el checklist 4.9 falle.

## Referencias

- Arquitectura de capas: `.claude/rules/ddd-layers.md`
- Convenciones de nombrado: `.claude/rules/naming.md`
- Agentes disponibles: `.claude/agents/`
- Skill de cobertura: `.claude/skills/coverage-gate/`
- Skill de imports: `.claude/skills/check-import-boundaries/`

## Resultado

Si todos los puntos pasan: confirmar que la tarea cumple el checklist.
Si alguno falla: no marcar como terminada. Reportar al subagente de la
capa afectada con el detalle exacto del fallo.

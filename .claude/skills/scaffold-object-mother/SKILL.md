---
name: scaffold-object-mother
description: Genera el esqueleto de un Object Mother para una entidad de dominio. Lee la entidad desde su archivo, extrae sus campos y produce una función <entidad>_object_mother en la ruta espejo de tests. Úsala cuando domain-agent o application-agent necesiten datos de prueba reutilizables, o cuando el usuario pida "crea el object mother de X", "genera el mother para la entidad Y", "necesito datos de prueba para Z".
triggers:
  - "crea el object mother"
  - "genera el mother"
  - "datos de prueba para"
  - "object mother de"
  - "scaffold-object-mother"
---

# Scaffold Object Mother

Genera una función `<entidad>_object_mother` lista para usar como fuente
de datos de prueba válidos y reutilizables para una entidad de dominio.

## Argumento de entrada

La **ruta al archivo de la entidad**. Ejemplo:
- `src/domain/entities.py`

Si el usuario nombra la entidad en lugar de la ruta, localiza el archivo
con `glob` antes de continuar.

## 1. Leer y analizar la entidad

Lee el archivo de la entidad. Identifica:

1. **Nombre de la clase** (p. ej. `Session`, `Alert`, `TranscriptionSegment`).
2. **Campos** — busca atributos de clase con anotación en Pydantic `BaseModel`
   o `@dataclass`.
3. **Tipos de cada campo** — extrae los tipos tal cual están en el código.
4. **Campos con valor por defecto** — distíngelos de los obligatorios.
5. **Factory method disponible** — si existe `from_raw_data`, el mother debe
   usarlo para construir instancias.

## 2. Determinar la ruta de destino

El mother vive en la ruta espejo de tests o en el directorio `tests/mothers/`
si el proyecto lo usa (detecta con `glob`):

```
# Si existe tests/mothers/ → depositar ahí:
tests/mothers/<entidad>_object_mother.py

# Si no → ruta espejo de la entidad:
tests/<dominio>/domain/<entidad>_object_mother.py
```

## 3. Generar la función

Sigue el patrón de función con parámetros con valores por defecto:

```python
from <ruta_de_importacion_de_la_entidad> import <NombreEntidad>
# Importa los tipos necesarios para los valores por defecto


def <entidad>_object_mother(
    <campo1>: <tipo> = <valor_por_defecto>,
    <campo2>: <tipo> = <valor_por_defecto>,
    # ... todos los campos de la entidad
) -> <NombreEntidad>:
    return <NombreEntidad>(
        <campo1>=<campo1>,
        <campo2>=<campo2>,
        # ...
    )
```

**Ejemplo ilustrativo:**

```python
from src.domain.entities import Finding


def finding_object_mother(
    id: str = "finding-001",
    category: str = "urbanismo",
    severity: str = "media",
    status: str = "requiere_revision",
    message: str = "Ocupación proyectada no justificada con plano asociado.",
) -> Finding:
    return Finding(
        id=id,
        category=category,
        severity=severity,
        status=status,
        message=message,
    )
```

El test solo declara lo que le importa:

```python
def test_finding_with_critical_severity_blocks_report():
    finding = finding_object_mother(severity="critica")
    ...
```

### Reglas para los valores por defecto

- Usa valores **representativos y legibles**, no genéricos (`""`, `0`, `None`):
  - `str` → nombre del campo como valor, p. ej. `"session-001"`, `"active"`.
  - `int` / `float` → valor mínimo válido o representativo (`1`, `1000.0`).
  - `bool` → el valor más común en producción (`True` para `active`).
  - `datetime` → fecha fija, nunca `now()`.
  - `list` → `[]` salvo que la entidad requiera al menos un elemento.
- No usar `None` en campos no opcionales.
- No generar datos que parezcan PII real (nombres, emails, DNIs reales).

## 4. Verificar que importa correctamente

```bash
<prefijo_venv>/python -c "
from <ruta_objeto_mother> import <entidad>_object_mother
obj = <entidad>_object_mother()
print('OK:', obj)
"
```

Si falla por un import incorrecto, corrígelo antes de reportar.

## 5. Resultado

Entrega:
1. Ruta exacta del archivo generado.
2. Firma de la función con todos sus parámetros.
3. Nota si hay campos complejos omitidos que el agente podría necesitar añadir.

## No Usar Cuando

Si ya existe un mother para la entidad — actualizar el existente en lugar
de generar uno nuevo.

## Controles PSI-12

Los valores por defecto del mother nunca deben ser datos reales de producción
(PII, credenciales, identificadores de clientes reales).

## Referencias

- Patrón Object Mother: `.claude/rules/testing.md` §Object Mothers
- Convenciones de nombrado: `.claude/rules/naming.md`
- Agentes que la invocan: `domain-agent`, `application-agent`

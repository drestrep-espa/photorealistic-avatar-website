# Convenciones de nombrado — guía del proyecto §6

## Tabla de convenciones

| Elemento | Convención | Ejemplo en este proyecto |
|---|---|---|
| Entidad de dominio | Nombre del concepto, PascalCase | `ParsedField`, `ModelFields`, `CompositeField` |
| Puerto (interfaz) | Rol + sufijo de rol, PascalCase | `LlmService`, `DataRepository`, `ConfigRepository`, `FileService`, `TextExtractor` |
| Adaptador concreto | **Prefijo de tecnología** + nombre del puerto | `BedrockLlmService`, `SqlAlchemyDataRepository`, `FileServiceS3`, `TextractTextExtractor`, `KAnonymizer` |
| Caso de uso | verbo_sustantivo, snake_case | `parse_inputs_and_send_to_queue`, `extract_fields`, `create_dynamic_table` |
| Excepción de dominio | NombreException, PascalCase | `FileNotFoundException`, `InsufficientRowsException`, `SchemaNotExistsException` |
| Test | `test_<lo que prueba>`, snake_case | `test_parsed_field_rejects_non_string_deidentifiable` |
| Object Mother | `<entidad>_object_mother` | `parsed_field_object_mother`, `model_fields_object_mother` |
| Fake (doble de prueba) | `Fake<Puerto>` | `FakeLlmService`, `FakeDataRepository`, `FakeFileService` |

## Regla del prefijo de tecnología

El prefijo del adaptador dice de un vistazo con qué tecnología está hecho.
Si mañana se cambia de Bedrock a OpenAI, se crea `OpenAiLlmService` sin
tocar el dominio ni los casos de uso.

Prefijos en uso en este proyecto: `SqlAlchemy`, `Bedrock`, `S3` / `FileService`,
`Textract`, `K` (k-anonymizer).

### Error frecuente

MAL: `LlmServiceBedrock`, `RepositoryDataSqlAlchemy` (sufijo de tecnología)
BIEN: `BedrockLlmService`, `SqlAlchemyDataRepository` (prefijo de tecnología)

## Regla de oro de nombrado

El nombre de las funciones debería de ser suficiente para entender lo que hace sin necesidad de usar comentarios.

## Controles PSI-12

- No nombrar parámetros o variables con términos que sugieran credenciales
  en texto plano: evitar `password_plain`, `raw_secret`, `api_key_string`.
  Usar nombres que expresen que el valor viene del entorno: `api_key_env`.
- Los adaptadores (prefijo de tecnología) son los únicos que conocen
  credenciales — su nombre debe dejar claro que es infraestructura concreta.

## Automatización de estas convenciones

- `/scaffold-fake` genera `Fake<Puerto>` siguiendo la convención automáticamente.
- `/scaffold-object-mother` genera `<entidad>_object_mother` con la convención
  de función y parámetros con valores por defecto representativos.
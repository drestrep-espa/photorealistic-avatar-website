# Nombrado

## Convenciones

| Elemento | Convención | Ejemplo |
|---|---|---|
| Entidad de dominio | Nombre del concepto, PascalCase | `ParsedField`, `ModelFields`, `CompositeField` |
| Puerto/interfaz | Rol más sufijo de rol, PascalCase | `LlmService`, `DataRepository`, `ConfigRepository`, `FileService`, `TextExtractor` |
| Adaptador concreto | Prefijo de tecnología más nombre del puerto | `BedrockLlmService`, `SqlAlchemyDataRepository`, `S3FileService`, `TextractTextExtractor` |
| Caso de uso | verbo_sustantivo, snake_case | `parse_inputs_and_send_to_queue`, `extract_fields`, `create_dynamic_table` |
| Excepción de dominio | NombreException, PascalCase | `FileNotFoundException`, `InsufficientRowsException`, `SchemaNotExistsException` |
| Test | `test_<comportamiento>`, snake_case | `test_parsed_field_rejects_non_string_deidentifiable` |
| Object Mother | `<entidad>_object_mother` | `parsed_field_object_mother` |
| Fake | `Fake<Port>` | `FakeLlmService`, `FakeDataRepository`, `FakeFileService` |

## Regla del prefijo de tecnología

El prefijo del adaptador indica qué tecnología implementa el puerto. Si Bedrock
se sustituye por OpenAI, crea `OpenAiLlmService` sin tocar dominio ni
aplicación.

Mal:

```text
LlmServiceBedrock
RepositoryDataSqlAlchemy
```

Bien:

```text
BedrockLlmService
SqlAlchemyDataRepository
```

Los nombres deberían hacer innecesarios los comentarios para el comportamiento
ordinario.

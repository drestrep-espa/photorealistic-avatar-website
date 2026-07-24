from typing import Any, Dict, List

from ..domain.project_document_search_service import ProjectDocumentSearchService

SEARCH_PROJECT_DOCUMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "search_project_document",
        "description": (
            "Busca fragmentos de texto por similitud semántica DENTRO DEL "
            "PROYECTO que se está revisando (memoria, tablas, anexos, "
            "certificados del propio proyecto básico), no en la normativa "
            "(para eso está search_item). Úsala cuando necesites localizar "
            "un dato concreto del proyecto que no quedó capturado en el "
            "plan inicial, por ejemplo un valor exacto que hay que comparar "
            "contra un parámetro urbanístico. No decide si el proyecto "
            "cumple, solo recupera fragmentos de texto del proyecto con su "
            "ubicación para que se puedan revisar."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Consulta en lenguaje natural sobre el dato del "
                        "proyecto que se quiere localizar (ej: 'superficie "
                        "construida total declarada en la memoria')."
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": (
                        "Número máximo de fragmentos del proyecto a "
                        "devolver. Si se omite, se usa el valor por "
                        "defecto."
                    ),
                },
            },
            "required": ["query"],
        },
    },
}


def search_project_document(
    *,
    project_document_search_service: ProjectDocumentSearchService,
    query: str,
    max_results: int = 8,
) -> List[Dict[str, Any]]:
    return project_document_search_service.search(query=query, max_results=max_results)

from typing import Any, Dict, List

from ..domain.normative_search_service import NormativeSearchService

SEARCH_ITEM_TOOL = {
    "type": "function",
    "function": {
        "name": "search_item",
        "description": (
            "Busca fragmentos de normativa urbanística relevantes por "
            "similitud semántica en la vector store de normativa indexada "
            "(PGOU, ordenanzas, planes parciales, CTE...), para consultar "
            "qué debe cumplir el proyecto. No decide si el proyecto cumple, "
            "solo recupera fragmentos de texto con su documento de origen "
            "para que se puedan revisar."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Consulta en lenguaje natural sobre la normativa que "
                        "se quiere localizar (ej: 'altura máxima edificación "
                        "unifamiliar aislada Boadilla del Monte')."
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": (
                        "Número máximo de fragmentos de normativa a "
                        "devolver. Si se omite, se usa el valor por defecto. "
                        "Si los fragmentos recuperados no son suficientes "
                        "para verificar un punto con evidencia concluyente, "
                        "aumenta max_results o repite la búsqueda con una "
                        "query más específica."
                    ),
                },
            },
            "required": ["query"],
        },
    },
}


def search_item(
    *,
    normative_search_service: NormativeSearchService,
    query: str,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    return normative_search_service.search(query=query, max_results=max_results)

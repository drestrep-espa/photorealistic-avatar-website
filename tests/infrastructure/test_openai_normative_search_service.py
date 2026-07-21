from types import SimpleNamespace
from unittest.mock import MagicMock

from src.infrastructure.openai_normative_search_service import (
    OpenAiNormativeSearchService,
)


def _build_fake_openai_client(data: list) -> MagicMock:
    fake_client = MagicMock()
    fake_response = SimpleNamespace(data=data, object="vector_store.search_results.page")
    fake_client.vector_stores.search.return_value = fake_response
    return fake_client


def _build_search_result(text: str, score: float, filename: str) -> SimpleNamespace:
    return SimpleNamespace(
        attributes=None,
        content=[SimpleNamespace(text=text, type="text")],
        file_id="file-123",
        filename=filename,
        score=score,
    )


def test_search_calls_client_with_query_and_max_results():
    fake_client = _build_fake_openai_client(
        [_build_search_result("altura maxima 3 plantas", 0.87, "pgou_boadilla.pdf")]
    )
    service = OpenAiNormativeSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_fake_123",
        client=fake_client,
    )

    service.search(query="altura maxima permitida", max_results=3)

    fake_client.vector_stores.search.assert_called_once_with(
        vector_store_id="vs_fake_123",
        query="altura maxima permitida",
        max_num_results=3,
    )


def test_search_uses_default_max_results_of_five():
    fake_client = _build_fake_openai_client([])
    service = OpenAiNormativeSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_fake_123",
        client=fake_client,
    )

    service.search(query="retranqueo minimo")

    fake_client.vector_stores.search.assert_called_once_with(
        vector_store_id="vs_fake_123",
        query="retranqueo minimo",
        max_num_results=5,
    )


def test_search_returns_normalized_fragments():
    fake_client = _build_fake_openai_client(
        [
            _build_search_result("altura maxima 3 plantas", 0.87, "pgou_boadilla.pdf"),
            _build_search_result("retranqueo minimo 3 metros", 0.65, "normas_urbanisticas.pdf"),
        ]
    )
    service = OpenAiNormativeSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_fake_123",
        client=fake_client,
    )

    result = service.search(query="altura maxima")

    assert result == [
        {
            "text": "altura maxima 3 plantas",
            "score": 0.87,
            "filename": "pgou_boadilla.pdf",
        },
        {
            "text": "retranqueo minimo 3 metros",
            "score": 0.65,
            "filename": "normas_urbanisticas.pdf",
        },
    ]


def test_search_joins_multiple_content_chunks_of_same_result():
    result_with_multiple_chunks = SimpleNamespace(
        attributes=None,
        content=[
            SimpleNamespace(text="parte 1 del articulo", type="text"),
            SimpleNamespace(text="parte 2 del articulo", type="text"),
        ],
        file_id="file-456",
        filename="pgou_boadilla.pdf",
        score=0.72,
    )
    fake_client = _build_fake_openai_client([result_with_multiple_chunks])
    service = OpenAiNormativeSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_fake_123",
        client=fake_client,
    )

    result = service.search(query="articulo edificabilidad")

    assert result == [
        {
            "text": "parte 1 del articulo\nparte 2 del articulo",
            "score": 0.72,
            "filename": "pgou_boadilla.pdf",
        }
    ]


def test_search_returns_empty_list_when_no_results():
    fake_client = _build_fake_openai_client([])
    service = OpenAiNormativeSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_fake_123",
        client=fake_client,
    )

    result = service.search(query="parametro inexistente")

    assert result == []


def test_openai_normative_search_service_inherits_from_port():
    from src.domain.normative_search_service import NormativeSearchService

    fake_client = _build_fake_openai_client([])
    service = OpenAiNormativeSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_fake_123",
        client=fake_client,
    )

    assert isinstance(service, NormativeSearchService)

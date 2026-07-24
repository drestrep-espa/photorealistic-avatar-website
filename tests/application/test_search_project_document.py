from tests.fakes.fake_project_document_search_service import (
    FakeProjectDocumentSearchService,
)

from src.application.search_project_document import search_project_document


def _fragments():
    return [
        {"text": "Superficie construida: 320 m2", "score": 0.93, "page": 4},
        {"text": "Número de plantas: 2", "score": 0.88, "page": 5},
    ]


def test_search_project_document_returns_fragments_from_the_port():
    fake_project_document_search_service = FakeProjectDocumentSearchService(
        response=_fragments()
    )

    result = search_project_document(
        project_document_search_service=fake_project_document_search_service,
        query="superficie construida total",
    )

    assert result == _fragments()


def test_search_project_document_passes_query_and_max_results_to_the_port():
    fake_project_document_search_service = FakeProjectDocumentSearchService(
        response=_fragments()
    )

    search_project_document(
        project_document_search_service=fake_project_document_search_service,
        query="número de plantas",
        max_results=3,
    )

    assert fake_project_document_search_service.received_query == "número de plantas"
    assert fake_project_document_search_service.received_max_results == 3


def test_search_project_document_uses_default_max_results_when_not_provided():
    fake_project_document_search_service = FakeProjectDocumentSearchService(
        response=_fragments()
    )

    search_project_document(
        project_document_search_service=fake_project_document_search_service,
        query="ocupación de parcela",
    )

    assert fake_project_document_search_service.received_max_results == 8

import pytest

from src.domain.project_document_search_service import ProjectDocumentSearchService
from tests.fakes.fake_project_document_search_service import (
    FakeProjectDocumentSearchService,
)


def test_project_document_search_service_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        ProjectDocumentSearchService()


def test_fake_project_document_search_service_index_document_stores_path():
    fake_project_document_search_service = FakeProjectDocumentSearchService()

    fake_project_document_search_service.index_document(document_path="/tmp/proyecto_boadilla.pdf")

    assert fake_project_document_search_service.received_document_path == "/tmp/proyecto_boadilla.pdf"


def test_fake_project_document_search_service_search_returns_default_empty_list():
    fake_project_document_search_service = FakeProjectDocumentSearchService()

    result = fake_project_document_search_service.search(query="superficie construida")

    assert result == []
    assert fake_project_document_search_service.received_query == "superficie construida"
    assert fake_project_document_search_service.received_max_results == 5


def test_fake_project_document_search_service_search_returns_configured_fragments():
    fragments = [
        {"text": "Superficie construida total: 250 m2", "score": 0.88, "filename": "proyecto_boadilla.pdf"},
        {"text": "Plano de emplazamiento, pagina 3", "score": None, "filename": None},
    ]
    fake_project_document_search_service = FakeProjectDocumentSearchService(response=fragments)

    result = fake_project_document_search_service.search(query="superficie", max_results=2)

    assert result == fragments
    assert fake_project_document_search_service.received_query == "superficie"
    assert fake_project_document_search_service.received_max_results == 2


def test_fake_project_document_search_service_delete_index_marks_flag():
    fake_project_document_search_service = FakeProjectDocumentSearchService()

    assert fake_project_document_search_service.was_index_deleted is False

    fake_project_document_search_service.delete_index()

    assert fake_project_document_search_service.was_index_deleted is True

from tests.fakes.fake_project_document_search_service import (
    FakeProjectDocumentSearchService,
)

from src.application.index_project_document import index_project_document


def test_index_project_document_calls_the_port_with_the_document_path():
    fake_project_document_search_service = FakeProjectDocumentSearchService()

    index_project_document(
        project_document_search_service=fake_project_document_search_service,
        document_path="/tmp/proyecto_basico.pdf",
    )

    assert (
        fake_project_document_search_service.received_document_path
        == "/tmp/proyecto_basico.pdf"
    )


def test_index_project_document_returns_none():
    fake_project_document_search_service = FakeProjectDocumentSearchService()

    result = index_project_document(
        project_document_search_service=fake_project_document_search_service,
        document_path="/tmp/proyecto_basico.pdf",
    )

    assert result is None

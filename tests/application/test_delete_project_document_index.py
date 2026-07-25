from tests.fakes.fake_project_document_search_service import (
    FakeProjectDocumentSearchService,
)

from src.application.delete_project_document_index import (
    delete_project_document_index,
)


def test_delete_project_document_index_marks_the_index_as_deleted():
    fake_project_document_search_service = FakeProjectDocumentSearchService()

    delete_project_document_index(
        project_document_search_service=fake_project_document_search_service,
    )

    assert fake_project_document_search_service.was_index_deleted is True


def test_delete_project_document_index_returns_none():
    fake_project_document_search_service = FakeProjectDocumentSearchService()

    result = delete_project_document_index(
        project_document_search_service=fake_project_document_search_service,
    )

    assert result is None

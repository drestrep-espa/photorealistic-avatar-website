from ..domain.project_document_search_service import ProjectDocumentSearchService


def delete_project_document_index(
    *, project_document_search_service: ProjectDocumentSearchService
) -> None:
    project_document_search_service.delete_index()

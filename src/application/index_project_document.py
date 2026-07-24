from ..domain.project_document_search_service import ProjectDocumentSearchService


def index_project_document(
    *,
    project_document_search_service: ProjectDocumentSearchService,
    document_path: str,
) -> None:
    project_document_search_service.index_document(document_path)

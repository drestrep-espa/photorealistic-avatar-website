from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

from src.infrastructure.openai_project_document_search_service import (
    OpenAiProjectDocumentSearchService,
)

MODULE = "src.infrastructure.openai_project_document_search_service"


def _build_fake_openai_client() -> MagicMock:
    fake_client = MagicMock()
    fake_client.files.create.return_value = SimpleNamespace(id="file-abc")
    fake_client.vector_stores.create.return_value = SimpleNamespace(id="vs_project_abc")
    fake_client.vector_stores.files.create_and_poll.return_value = SimpleNamespace(
        id="vsf-abc", status="completed"
    )
    return fake_client


def _build_search_result(
    text: str, score: float, filename: str, page: int = None
) -> SimpleNamespace:
    return SimpleNamespace(
        attributes={"page": page} if page is not None else None,
        content=[SimpleNamespace(text=text, type="text")],
        file_id="file-123",
        filename=filename,
        score=score,
    )


def test_index_document_uploads_file_and_creates_vector_store():
    fake_client = _build_fake_openai_client()
    service = OpenAiProjectDocumentSearchService(api_key="fake-api-key", client=fake_client)

    with patch("builtins.open", mock_open(read_data=b"%PDF-1.4 contenido")):
        service.index_document("/tmp/proyecto_boadilla.pdf")

    fake_client.files.create.assert_called_once()
    _, upload_kwargs = fake_client.files.create.call_args
    assert upload_kwargs["purpose"] == "assistants"

    fake_client.vector_stores.create.assert_called_once()
    _, create_kwargs = fake_client.vector_stores.create.call_args
    assert create_kwargs["name"] == "proyecto_boadilla.pdf"

    fake_client.vector_stores.files.create_and_poll.assert_called_once_with(
        vector_store_id="vs_project_abc",
        file_id="file-abc",
    )


def test_index_document_stores_vector_store_id_for_later_search():
    fake_client = _build_fake_openai_client()
    fake_client.vector_stores.search.return_value = SimpleNamespace(
        data=[_build_search_result("altura maxima 3 plantas", 0.9, "proyecto_boadilla.pdf")],
        object="vector_store.search_results.page",
    )
    service = OpenAiProjectDocumentSearchService(api_key="fake-api-key", client=fake_client)

    with patch("builtins.open", mock_open(read_data=b"%PDF-1.4 contenido")):
        service.index_document("/tmp/proyecto_boadilla.pdf")

    service.search(query="altura maxima", max_results=2)

    fake_client.vector_stores.search.assert_called_once_with(
        vector_store_id="vs_project_abc",
        query="altura maxima",
        max_num_results=2,
    )


def test_search_returns_normalized_fragments_with_page():
    fake_client = _build_fake_openai_client()
    fake_client.vector_stores.search.return_value = SimpleNamespace(
        data=[
            _build_search_result(
                "retranqueo minimo 3 metros", 0.65, "proyecto_boadilla.pdf", page=4
            )
        ],
        object="vector_store.search_results.page",
    )
    service = OpenAiProjectDocumentSearchService(api_key="fake-api-key", client=fake_client)

    with patch("builtins.open", mock_open(read_data=b"%PDF-1.4 contenido")):
        service.index_document("/tmp/proyecto_boadilla.pdf")

    result = service.search(query="retranqueo minimo")

    assert result == [
        {
            "text": "retranqueo minimo 3 metros",
            "score": 0.65,
            "filename": "proyecto_boadilla.pdf",
            "page": 4,
        }
    ]


def test_search_returns_none_page_when_attributes_missing():
    fake_client = _build_fake_openai_client()
    fake_client.vector_stores.search.return_value = SimpleNamespace(
        data=[_build_search_result("altura maxima 3 plantas", 0.9, "proyecto_boadilla.pdf")],
        object="vector_store.search_results.page",
    )
    service = OpenAiProjectDocumentSearchService(api_key="fake-api-key", client=fake_client)

    with patch("builtins.open", mock_open(read_data=b"%PDF-1.4 contenido")):
        service.index_document("/tmp/proyecto_boadilla.pdf")

    result = service.search(query="altura maxima")

    assert result == [
        {
            "text": "altura maxima 3 plantas",
            "score": 0.9,
            "filename": "proyecto_boadilla.pdf",
            "page": None,
        }
    ]


def test_search_uses_default_max_results_of_five():
    fake_client = _build_fake_openai_client()
    fake_client.vector_stores.search.return_value = SimpleNamespace(
        data=[], object="vector_store.search_results.page"
    )
    service = OpenAiProjectDocumentSearchService(api_key="fake-api-key", client=fake_client)

    with patch("builtins.open", mock_open(read_data=b"%PDF-1.4 contenido")):
        service.index_document("/tmp/proyecto_boadilla.pdf")

    service.search(query="edificabilidad")

    fake_client.vector_stores.search.assert_called_once_with(
        vector_store_id="vs_project_abc",
        query="edificabilidad",
        max_num_results=5,
    )


def test_search_works_with_preexisting_vector_store_id_without_indexing():
    fake_client = _build_fake_openai_client()
    fake_client.vector_stores.search.return_value = SimpleNamespace(
        data=[_build_search_result("altura maxima 3 plantas", 0.9, "proyecto_boadilla.pdf", page=1)],
        object="vector_store.search_results.page",
    )
    service = OpenAiProjectDocumentSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_existente",
        client=fake_client,
    )

    result = service.search(query="altura maxima")

    fake_client.vector_stores.create.assert_not_called()
    fake_client.files.create.assert_not_called()
    fake_client.vector_stores.search.assert_called_once_with(
        vector_store_id="vs_existente",
        query="altura maxima",
        max_num_results=5,
    )
    assert result == [
        {
            "text": "altura maxima 3 plantas",
            "score": 0.9,
            "filename": "proyecto_boadilla.pdf",
            "page": 1,
        }
    ]


def test_index_document_deletes_previous_index_before_creating_new_one():
    fake_client = _build_fake_openai_client()
    fake_client.vector_stores.files.list.return_value = [
        SimpleNamespace(id="old-file-1"),
        SimpleNamespace(id="old-file-2"),
    ]
    service = OpenAiProjectDocumentSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_old",
        client=fake_client,
    )

    with patch("builtins.open", mock_open(read_data=b"%PDF-1.4 contenido")):
        service.index_document("/tmp/proyecto_boadilla.pdf")

    fake_client.vector_stores.files.list.assert_called_once_with(
        vector_store_id="vs_old"
    )
    fake_client.files.delete.assert_any_call("old-file-1")
    fake_client.files.delete.assert_any_call("old-file-2")
    fake_client.vector_stores.delete.assert_called_once_with("vs_old")
    fake_client.vector_stores.create.assert_called_once()


def test_index_document_does_not_delete_anything_on_first_indexing():
    fake_client = _build_fake_openai_client()
    service = OpenAiProjectDocumentSearchService(api_key="fake-api-key", client=fake_client)

    with patch("builtins.open", mock_open(read_data=b"%PDF-1.4 contenido")):
        service.index_document("/tmp/proyecto_boadilla.pdf")

    fake_client.vector_stores.files.list.assert_not_called()
    fake_client.files.delete.assert_not_called()
    fake_client.vector_stores.delete.assert_not_called()


def test_delete_index_deletes_files_and_vector_store_and_is_idempotent():
    fake_client = _build_fake_openai_client()
    fake_client.vector_stores.files.list.return_value = [
        SimpleNamespace(id="file-1"),
        SimpleNamespace(id="file-2"),
    ]
    service = OpenAiProjectDocumentSearchService(
        api_key="fake-api-key",
        vector_store_id="vs_old",
        client=fake_client,
    )

    service.delete_index()

    fake_client.vector_stores.files.list.assert_called_once_with(
        vector_store_id="vs_old"
    )
    fake_client.files.delete.assert_any_call("file-1")
    fake_client.files.delete.assert_any_call("file-2")
    fake_client.vector_stores.delete.assert_called_once_with("vs_old")

    service.delete_index()

    fake_client.vector_stores.delete.assert_called_once_with("vs_old")


def test_delete_index_is_a_no_op_when_nothing_indexed():
    fake_client = _build_fake_openai_client()
    service = OpenAiProjectDocumentSearchService(api_key="fake-api-key", client=fake_client)

    service.delete_index()

    fake_client.vector_stores.files.list.assert_not_called()
    fake_client.files.delete.assert_not_called()
    fake_client.vector_stores.delete.assert_not_called()


def test_openai_project_document_search_service_inherits_from_port():
    from src.domain.project_document_search_service import ProjectDocumentSearchService

    fake_client = _build_fake_openai_client()
    service = OpenAiProjectDocumentSearchService(api_key="fake-api-key", client=fake_client)

    assert isinstance(service, ProjectDocumentSearchService)

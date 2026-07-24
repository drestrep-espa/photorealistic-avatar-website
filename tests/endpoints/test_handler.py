from unittest.mock import MagicMock, patch

from src.application.build_review_plan import BUILD_REVIEW_PLAN_TOOL
from src.application.search_item import SEARCH_ITEM_TOOL
from src.application.search_project_document import SEARCH_PROJECT_DOCUMENT_TOOL
from src.endpoints.handler import check_document


def _set_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-api-key")
    monkeypatch.setenv("NORMATIVE_VECTOR_STORE_ID", "fake-vector-store-id")
    monkeypatch.delenv("PROJECT_DOCUMENT_VECTOR_STORE_ID", raising=False)


@patch("src.endpoints.handler.OpenAiLlmCostTracker")
@patch("src.endpoints.handler.check_document_with_agent")
@patch("src.endpoints.handler.Agent")
@patch("src.endpoints.handler.index_project_document")
@patch("src.endpoints.handler.OpenAiProjectDocumentSearchService")
@patch("src.endpoints.handler.OpenAiNormativeSearchService")
@patch("src.endpoints.handler.OpenAiLlmService")
def test_check_document_builds_agent_with_the_three_tools_registered(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    mock_check_document_with_agent.return_value = "resultado final"
    mock_cost_tracker_cls.return_value.summary.return_value = {"total_cost_usd": 0.0}

    result = check_document("proyecto.pdf")

    mock_agent_cls.assert_called_once()
    _, kwargs = mock_agent_cls.call_args
    tools = kwargs["tools"]
    tool_executors = kwargs["tool_executors"]

    assert tools == [BUILD_REVIEW_PLAN_TOOL, SEARCH_ITEM_TOOL, SEARCH_PROJECT_DOCUMENT_TOOL]
    assert set(tool_executors.keys()) == {
        "build_review_plan",
        "search_item",
        "search_project_document",
    }

    mock_check_document_with_agent.assert_called_once_with(mock_agent_cls.return_value)
    assert result == ("resultado final", {"total_cost_usd": 0.0})


@patch("src.endpoints.handler.OpenAiLlmCostTracker")
@patch("src.endpoints.handler.check_document_with_agent")
@patch("src.endpoints.handler.Agent")
@patch("src.endpoints.handler.index_project_document")
@patch("src.endpoints.handler.OpenAiProjectDocumentSearchService")
@patch("src.endpoints.handler.OpenAiNormativeSearchService")
@patch("src.endpoints.handler.OpenAiLlmService")
def test_check_document_indexes_project_document_before_building_the_agent(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)

    call_order = []
    mock_index_project_document.side_effect = lambda **kwargs: call_order.append("index")
    mock_agent_cls.side_effect = lambda *a, **kw: call_order.append("agent") or MagicMock()

    check_document("proyecto.pdf")

    assert call_order == ["index", "agent"]
    mock_index_project_document.assert_called_once_with(
        project_document_search_service=mock_project_document_search_cls.return_value,
        document_path="proyecto.pdf",
    )


@patch("src.endpoints.handler.OpenAiLlmCostTracker")
@patch("src.endpoints.handler.check_document_with_agent")
@patch("src.endpoints.handler.Agent")
@patch("src.endpoints.handler.index_project_document")
@patch("src.endpoints.handler.OpenAiProjectDocumentSearchService")
@patch("src.endpoints.handler.OpenAiNormativeSearchService")
@patch("src.endpoints.handler.OpenAiLlmService")
def test_check_document_reads_credentials_and_config_from_environment(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)

    check_document("proyecto.pdf")

    mock_llm_service_cls.assert_called_once_with(
        api_key="fake-api-key", cost_tracker=mock_cost_tracker_cls.return_value
    )
    mock_normative_search_cls.assert_called_once_with(
        api_key="fake-api-key", vector_store_id="fake-vector-store-id"
    )
    mock_project_document_search_cls.assert_called_once_with(api_key="fake-api-key")


@patch("src.endpoints.handler.OpenAiLlmCostTracker")
@patch("src.endpoints.handler.build_review_plan")
@patch("src.endpoints.handler.check_document_with_agent")
@patch("src.endpoints.handler.Agent")
@patch("src.endpoints.handler.index_project_document")
@patch("src.endpoints.handler.OpenAiProjectDocumentSearchService")
@patch("src.endpoints.handler.OpenAiNormativeSearchService")
@patch("src.endpoints.handler.OpenAiLlmService")
def test_build_review_plan_executor_calls_build_review_plan_with_document_path(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_build_review_plan,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    mock_build_review_plan.return_value = {}

    check_document("proyecto.pdf")

    _, kwargs = mock_agent_cls.call_args
    tool_executors = kwargs["tool_executors"]

    tool_executors["build_review_plan"]({"unexpected": "arg"})

    mock_build_review_plan.assert_called_once_with(
        llm_service=mock_llm_service_cls.return_value, document_path="proyecto.pdf"
    )


@patch("src.endpoints.handler.OpenAiLlmCostTracker")
@patch("src.endpoints.handler.check_document_with_agent")
@patch("src.endpoints.handler.Agent")
@patch("src.endpoints.handler.index_project_document")
@patch("src.endpoints.handler.OpenAiProjectDocumentSearchService")
@patch("src.endpoints.handler.OpenAiNormativeSearchService")
@patch("src.endpoints.handler.OpenAiLlmService")
def test_search_item_executor_forwards_query_and_max_results(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    mock_normative_search_cls.return_value.search.return_value = [{"text": "frag"}]

    check_document("proyecto.pdf")

    _, kwargs = mock_agent_cls.call_args
    tool_executors = kwargs["tool_executors"]

    result = tool_executors["search_item"]({"query": "altura máxima", "max_results": 3})

    mock_normative_search_cls.return_value.search.assert_called_once_with(
        query="altura máxima", max_results=3
    )
    assert result == [{"text": "frag"}]


@patch("src.endpoints.handler.OpenAiLlmCostTracker")
@patch("src.endpoints.handler.check_document_with_agent")
@patch("src.endpoints.handler.Agent")
@patch("src.endpoints.handler.index_project_document")
@patch("src.endpoints.handler.OpenAiProjectDocumentSearchService")
@patch("src.endpoints.handler.OpenAiNormativeSearchService")
@patch("src.endpoints.handler.OpenAiLlmService")
def test_search_project_document_executor_forwards_query_with_default_max_results(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    mock_project_document_search_cls.return_value.search.return_value = [{"text": "frag"}]

    check_document("proyecto.pdf")

    _, kwargs = mock_agent_cls.call_args
    tool_executors = kwargs["tool_executors"]

    result = tool_executors["search_project_document"]({"query": "superficie construida"})

    mock_project_document_search_cls.return_value.search.assert_called_once_with(
        query="superficie construida", max_results=8
    )
    assert result == [{"text": "frag"}]


@patch("src.endpoints.handler.OpenAiLlmCostTracker")
@patch("src.endpoints.handler.check_document_with_agent")
@patch("src.endpoints.handler.Agent")
@patch("src.endpoints.handler.index_project_document")
@patch("src.endpoints.handler.OpenAiProjectDocumentSearchService")
@patch("src.endpoints.handler.OpenAiNormativeSearchService")
@patch("src.endpoints.handler.OpenAiLlmService")
def test_check_document_reuses_existing_vector_store_and_skips_indexing(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    monkeypatch.setenv("PROJECT_DOCUMENT_VECTOR_STORE_ID", "existing-vector-store-id")

    check_document("proyecto.pdf")

    mock_project_document_search_cls.assert_called_once_with(
        api_key="fake-api-key", vector_store_id="existing-vector-store-id"
    )
    mock_index_project_document.assert_not_called()


@patch("src.endpoints.handler.OpenAiLlmCostTracker")
@patch("src.endpoints.handler.check_document_with_agent")
@patch("src.endpoints.handler.Agent")
@patch("src.endpoints.handler.index_project_document")
@patch("src.endpoints.handler.OpenAiProjectDocumentSearchService")
@patch("src.endpoints.handler.OpenAiNormativeSearchService")
@patch("src.endpoints.handler.OpenAiLlmService")
def test_check_document_indexes_when_no_vector_store_id_configured(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)

    check_document("proyecto.pdf")

    mock_project_document_search_cls.assert_called_once_with(api_key="fake-api-key")
    mock_index_project_document.assert_called_once_with(
        project_document_search_service=mock_project_document_search_cls.return_value,
        document_path="proyecto.pdf",
    )

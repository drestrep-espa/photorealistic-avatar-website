from unittest.mock import MagicMock, patch

import pytest

from src.application.build_review_plan import BUILD_REVIEW_PLAN_TOOL
from src.application.search_item import SEARCH_ITEM_TOOL
from src.application.search_project_document import SEARCH_PROJECT_DOCUMENT_TOOL
from src.endpoints.handler import check_document


def _set_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-api-key")
    monkeypatch.setenv("VECTOR_STORE_id", "fake-vector-store-id")
    monkeypatch.delenv("PROJECT_DOCUMENT_VECTOR_STORE_ID", raising=False)


def _patch_all(func):
    decorators = [
        patch("src.endpoints.handler.OpenAiLlmCostTracker"),
        patch("src.endpoints.handler.check_document_with_agent"),
        patch("src.endpoints.handler.Agent"),
        patch("src.endpoints.handler.generate_review_report"),
        patch("src.endpoints.handler.FpdfReportGenerator"),
        patch("src.endpoints.handler.delete_project_document_index"),
        patch("src.endpoints.handler.index_project_document"),
        patch("src.endpoints.handler.OpenAiProjectDocumentSearchService"),
        patch("src.endpoints.handler.OpenAiNormativeSearchService"),
        patch("src.endpoints.handler.OpenAiLlmService"),
    ]
    for decorator in reversed(decorators):
        func = decorator(func)
    return func


@_patch_all
def test_check_document_builds_agent_with_the_three_tools_registered(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    mock_check_document_with_agent.return_value = "resultado final"
    mock_generate_review_report.return_value = "data/informe/informe.pdf"
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
    assert result == {
        "summary": "resultado final",
        "report_path": "data/informe/informe.pdf",
        "cost_summary": {"total_cost_usd": 0.0},
    }


@_patch_all
def test_check_document_reads_credentials_and_config_from_environment(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
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


@_patch_all
def test_check_document_uses_explicit_credentials_when_provided(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
):
    check_document(
        "proyecto.pdf",
        api_key="ssm-api-key",
        vector_store_id="ssm-vector-store-id",
    )

    mock_llm_service_cls.assert_called_once_with(
        api_key="ssm-api-key",
        cost_tracker=mock_cost_tracker_cls.return_value,
    )
    mock_normative_search_cls.assert_called_once_with(
        api_key="ssm-api-key",
        vector_store_id="ssm-vector-store-id",
    )
    mock_project_document_search_cls.assert_called_once_with(api_key="ssm-api-key")


@_patch_all
def test_build_review_plan_executor_calls_build_review_plan_with_document_path(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)

    with patch("src.endpoints.handler.build_review_plan") as mock_build_review_plan:
        mock_build_review_plan.return_value = {}

        check_document("proyecto.pdf")

        _, kwargs = mock_agent_cls.call_args
        tool_executors = kwargs["tool_executors"]

        tool_executors["build_review_plan"]({"unexpected": "arg"})

        mock_build_review_plan.assert_called_once_with(
            llm_service=mock_llm_service_cls.return_value, document_path="proyecto.pdf"
        )


@_patch_all
def test_search_item_executor_forwards_query_and_max_results(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
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

    result = tool_executors["search_item"]({"query": "altura máxima", "max_results": 20})

    mock_normative_search_cls.return_value.search.assert_called_once_with(
        query="altura máxima", max_results=20
    )
    assert result == [{"text": "frag"}]


@_patch_all
def test_search_item_executor_enforces_minimum_of_15_results(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)

    check_document("proyecto.pdf")

    _, kwargs = mock_agent_cls.call_args
    tool_executors = kwargs["tool_executors"]

    tool_executors["search_item"]({"query": "retranqueos", "max_results": 3})

    mock_normative_search_cls.return_value.search.assert_called_once_with(
        query="retranqueos", max_results=15
    )


@_patch_all
def test_search_item_executor_defaults_to_15_results_when_max_results_omitted(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)

    check_document("proyecto.pdf")

    _, kwargs = mock_agent_cls.call_args
    tool_executors = kwargs["tool_executors"]

    tool_executors["search_item"]({"query": "edificabilidad"})

    mock_normative_search_cls.return_value.search.assert_called_once_with(
        query="edificabilidad", max_results=15
    )


@_patch_all
def test_search_project_document_executor_forwards_query_with_default_max_results(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
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


@_patch_all
def test_check_document_ignores_preexisting_vector_store_env_and_indexes_a_fresh_one(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    monkeypatch.setenv("PROJECT_DOCUMENT_VECTOR_STORE_ID", "existing-vector-store-id")

    check_document("proyecto.pdf")

    mock_project_document_search_cls.assert_called_once_with(api_key="fake-api-key")
    mock_index_project_document.assert_called_once_with(
        project_document_search_service=mock_project_document_search_cls.return_value,
        document_path="proyecto.pdf",
    )


@_patch_all
def test_check_document_always_indexes_project_document_when_no_vector_store_id_configured(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
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


@_patch_all
def test_check_document_generates_report_with_agent_result_and_expected_output_dir(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    mock_check_document_with_agent.return_value = "resultado final"
    mock_generate_review_report.return_value = "data/informe/informe.pdf"

    check_document("proyecto.pdf")

    mock_generate_review_report.assert_called_once_with(
        report_generator=mock_fpdf_report_generator_cls.return_value,
        content="resultado final",
        output_dir="data/informe",
    )


@_patch_all
def test_check_document_uses_custom_report_output_dir(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    mock_check_document_with_agent.return_value = "resultado final"
    mock_generate_review_report.return_value = "/tmp/reports/informe.pdf"

    check_document("proyecto.pdf", report_output_dir="/tmp/reports")

    mock_generate_review_report.assert_called_once_with(
        report_generator=mock_fpdf_report_generator_cls.return_value,
        content="resultado final",
        output_dir="/tmp/reports",
    )


@_patch_all
def test_check_document_deletes_project_document_index_after_generating_report_in_order(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)

    call_order = []
    mock_index_project_document.side_effect = lambda **kwargs: call_order.append("index")
    mock_check_document_with_agent.side_effect = lambda agent: call_order.append("agent") or "ok"
    mock_generate_review_report.side_effect = (
        lambda **kwargs: call_order.append("generate_review_report")
        or "data/informe/informe.pdf"
    )
    mock_delete_project_document_index.side_effect = lambda **kwargs: call_order.append("delete")

    check_document("proyecto.pdf")

    assert call_order == ["index", "agent", "generate_review_report", "delete"]
    mock_delete_project_document_index.assert_called_once_with(
        project_document_search_service=mock_project_document_search_cls.return_value
    )


@_patch_all
def test_check_document_deletes_project_document_index_even_if_agent_raises(
    mock_llm_service_cls,
    mock_normative_search_cls,
    mock_project_document_search_cls,
    mock_index_project_document,
    mock_delete_project_document_index,
    mock_fpdf_report_generator_cls,
    mock_generate_review_report,
    mock_agent_cls,
    mock_check_document_with_agent,
    mock_cost_tracker_cls,
    monkeypatch,
):
    _set_env(monkeypatch)
    mock_check_document_with_agent.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        check_document("proyecto.pdf")

    mock_delete_project_document_index.assert_called_once_with(
        project_document_search_service=mock_project_document_search_cls.return_value
    )
    mock_generate_review_report.assert_not_called()

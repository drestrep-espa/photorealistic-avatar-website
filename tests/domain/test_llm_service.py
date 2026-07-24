import pytest

from src.domain.llm_service import LlmService
from tests.fakes.fake_llm_service import FakeLlmService


def test_llm_service_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        LlmService()


def test_fake_llm_service_make_request_returns_normalized_dict_without_tools():
    fake_llm_service = FakeLlmService(
        response={"content": "hola", "tool_calls": []}
    )
    messages = [{"role": "user", "content": "hola"}]

    result = fake_llm_service.make_request(messages=messages)

    assert result == {"content": "hola", "tool_calls": []}
    assert fake_llm_service.received_messages == messages
    assert fake_llm_service.received_tools is None


def test_fake_llm_service_make_request_returns_tool_calls_when_tools_provided():
    tool_calls = [{"id": "call_1", "name": "retrieve_normative", "arguments": "{}"}]
    fake_llm_service = FakeLlmService(response={"content": None, "tool_calls": tool_calls})
    messages = [{"role": "user", "content": "busca normativa"}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "retrieve_normative",
                "description": "Recupera normativa aplicable",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]

    result = fake_llm_service.make_request(messages=messages, tools=tools)

    assert result["content"] is None
    assert result["tool_calls"] == tool_calls
    assert fake_llm_service.received_tools == tools


def test_fake_llm_service_make_request_accepts_optional_document_path():
    expected_plan = {"content": '{"checks": []}', "tool_calls": []}
    fake_llm_service = FakeLlmService(response=expected_plan)
    messages = [{"role": "user", "content": "Genera un plan de revision con los checks aplicables"}]

    result = fake_llm_service.make_request(
        messages=messages,
        document_path="/tmp/proyecto_basico.pdf",
    )

    assert result == expected_plan
    assert fake_llm_service.received_messages == messages
    assert fake_llm_service.received_document_path == "/tmp/proyecto_basico.pdf"


def test_fake_llm_service_make_request_document_path_defaults_to_none():
    fake_llm_service = FakeLlmService()
    messages = [{"role": "user", "content": "busca normativa"}]

    fake_llm_service.make_request(messages=messages)

    assert fake_llm_service.received_document_path is None


def test_fake_llm_service_make_request_expects_json_defaults_to_false():
    fake_llm_service = FakeLlmService()
    messages = [{"role": "user", "content": "Genera un plan de revision"}]

    fake_llm_service.make_request(messages=messages)

    assert fake_llm_service.received_expects_json is False


def test_fake_llm_service_make_request_registers_expects_json_true():
    expected_plan = {"content": '{"checks": []}', "tool_calls": []}
    fake_llm_service = FakeLlmService(response=expected_plan)
    messages = [{"role": "user", "content": "Genera un plan de revision en JSON"}]

    result = fake_llm_service.make_request(messages=messages, expects_json=True)

    assert result == expected_plan
    assert fake_llm_service.received_expects_json is True

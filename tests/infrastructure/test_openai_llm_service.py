import base64
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.infrastructure.openai_llm_service import OpenAiLlmService


def _build_fake_openai_client(message: SimpleNamespace) -> MagicMock:
    fake_client = MagicMock()
    fake_response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
    fake_client.chat.completions.create.return_value = fake_response
    return fake_client


def test_openai_llm_service_uses_default_model():
    fake_client = _build_fake_openai_client(
        SimpleNamespace(content="hola", tool_calls=None)
    )

    service = OpenAiLlmService(api_key="fake-api-key", client=fake_client)

    assert service._model == "gpt-5.4-mini"


def test_make_request_returns_normalized_dict_without_tool_calls():
    fake_client = _build_fake_openai_client(
        SimpleNamespace(content="hola, esto es una respuesta", tool_calls=None)
    )
    service = OpenAiLlmService(api_key="fake-api-key", client=fake_client)
    messages = [{"role": "user", "content": "hola"}]

    result = service.make_request(messages=messages)

    assert result == {"content": "hola, esto es una respuesta", "tool_calls": []}
    fake_client.chat.completions.create.assert_called_once_with(
        model="gpt-5.4-mini", messages=messages, tools=None
    )


def test_make_request_returns_normalized_tool_calls_when_present():
    tool_call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(
            name="retrieve_normative", arguments='{"query": "altura maxima"}'
        ),
    )
    fake_client = _build_fake_openai_client(
        SimpleNamespace(content=None, tool_calls=[tool_call])
    )
    service = OpenAiLlmService(
        api_key="fake-api-key", model="gpt-5.4-mini", client=fake_client
    )
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

    result = service.make_request(messages=messages, tools=tools)

    assert result == {
        "content": None,
        "tool_calls": [
            {
                "id": "call_1",
                "name": "retrieve_normative",
                "arguments": '{"query": "altura maxima"}',
            }
        ],
    }
    fake_client.chat.completions.create.assert_called_once_with(
        model="gpt-5.4-mini", messages=messages, tools=tools
    )


def test_make_request_with_document_path_attaches_pdf_as_file_content_part(tmp_path):
    pdf_bytes = b"%PDF-1.4 fake pdf content with plans and text"
    pdf_path = tmp_path / "proyecto_basico.pdf"
    pdf_path.write_bytes(pdf_bytes)

    fake_client = _build_fake_openai_client(
        SimpleNamespace(content="analizado", tool_calls=None)
    )
    service = OpenAiLlmService(api_key="fake-api-key", client=fake_client)
    messages = [{"role": "user", "content": "analiza este proyecto"}]

    result = service.make_request(messages=messages, document_path=str(pdf_path))

    assert result == {"content": "analizado", "tool_calls": []}
    fake_client.chat.completions.create.assert_called_once()
    call_kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-5.4-mini"
    assert call_kwargs["tools"] is None

    sent_messages = call_kwargs["messages"]
    assert len(sent_messages) == 1
    sent_content = sent_messages[0]["content"]
    assert sent_content[0] == {"type": "text", "text": "analiza este proyecto"}

    file_part = sent_content[1]
    assert file_part["type"] == "file"
    assert file_part["file"]["filename"] == "proyecto_basico.pdf"
    expected_encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    assert (
        file_part["file"]["file_data"]
        == f"data:application/pdf;base64,{expected_encoded}"
    )


def test_make_request_with_document_path_does_not_mutate_original_messages(tmp_path):
    pdf_path = tmp_path / "planos.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 planos")

    fake_client = _build_fake_openai_client(
        SimpleNamespace(content="ok", tool_calls=None)
    )
    service = OpenAiLlmService(api_key="fake-api-key", client=fake_client)
    original_messages = [{"role": "user", "content": "revisa los planos"}]

    service.make_request(messages=original_messages, document_path=str(pdf_path))

    assert original_messages == [{"role": "user", "content": "revisa los planos"}]


def test_make_request_without_document_path_keeps_previous_behavior():
    fake_client = _build_fake_openai_client(
        SimpleNamespace(content="hola", tool_calls=None)
    )
    service = OpenAiLlmService(api_key="fake-api-key", client=fake_client)
    messages = [{"role": "user", "content": "hola"}]

    result = service.make_request(messages=messages, document_path=None)

    assert result == {"content": "hola", "tool_calls": []}
    fake_client.chat.completions.create.assert_called_once_with(
        model="gpt-5.4-mini", messages=messages, tools=None
    )


def test_make_request_with_expects_json_true_forces_json_response_format():
    fake_client = _build_fake_openai_client(
        SimpleNamespace(content='{"ok": true}', tool_calls=None)
    )
    service = OpenAiLlmService(api_key="fake-api-key", client=fake_client)
    messages = [{"role": "user", "content": "devuelve json"}]

    result = service.make_request(messages=messages, expects_json=True)

    assert result == {"content": '{"ok": true}', "tool_calls": []}
    fake_client.chat.completions.create.assert_called_once_with(
        model=service._model,
        messages=messages,
        tools=None,
        response_format={"type": "json_object"},
    )


def test_make_request_with_expects_json_false_omits_response_format():
    fake_client = _build_fake_openai_client(
        SimpleNamespace(content="hola", tool_calls=None)
    )
    service = OpenAiLlmService(api_key="fake-api-key", client=fake_client)
    messages = [{"role": "user", "content": "hola"}]

    result = service.make_request(messages=messages, expects_json=False)

    assert result == {"content": "hola", "tool_calls": []}
    call_kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert "response_format" not in call_kwargs
    fake_client.chat.completions.create.assert_called_once_with(
        model=service._model, messages=messages, tools=None
    )


def test_openai_llm_service_inherits_from_llm_service_port():
    from src.domain.llm_service import LlmService

    fake_client = _build_fake_openai_client(
        SimpleNamespace(content="hola", tool_calls=None)
    )
    service = OpenAiLlmService(api_key="fake-api-key", client=fake_client)

    assert isinstance(service, LlmService)

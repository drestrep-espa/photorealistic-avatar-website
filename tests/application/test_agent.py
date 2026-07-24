import pytest

from tests.fakes.fake_llm_service import FakeLlmService

from src.infrastructure.agent import Agent


def test_agent_returns_final_text_when_llm_responds_without_tool_calls():
    fake_llm_service = FakeLlmService(
        response={"content": "respuesta del asistente", "tool_calls": []}
    )
    agent = Agent(llm_service=fake_llm_service)

    result = agent.ask("hola")

    assert result == "respuesta del asistente"


def test_agent_tags_its_own_reasoning_calls_with_agent_reasoning_tool_name():
    fake_llm_service = FakeLlmService(
        response={"content": "respuesta del asistente", "tool_calls": []}
    )
    agent = Agent(llm_service=fake_llm_service)

    agent.ask("hola")

    assert fake_llm_service.received_tool_name == "agent_reasoning"


def test_agent_executes_tool_and_returns_final_text_after_second_round():
    tool_calls = [
        {"id": "call_1", "name": "buscar_normativa", "arguments": '{"municipio": "Boadilla"}'}
    ]
    fake_llm_service = FakeLlmService(
        responses=[
            {"content": None, "tool_calls": tool_calls},
            {"content": "normativa encontrada: PGOU Boadilla", "tool_calls": []},
        ]
    )
    tools = [{"name": "buscar_normativa"}]
    received_arguments = {}

    def buscar_normativa_executor(arguments):
        received_arguments.update(arguments)
        return {"normativa": "PGOU Boadilla"}

    agent = Agent(
        llm_service=fake_llm_service,
        tools=tools,
        tool_executors={"buscar_normativa": buscar_normativa_executor},
    )

    result = agent.ask("busca la normativa aplicable")

    assert result == "normativa encontrada: PGOU Boadilla"
    assert received_arguments == {"municipio": "Boadilla"}

    second_call_messages = fake_llm_service.received_messages_per_call[1]
    assert {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "buscar_normativa", "arguments": '{"municipio": "Boadilla"}'},
            }
        ],
    } in second_call_messages
    assert {
        "role": "tool",
        "tool_call_id": "call_1",
        "content": '{"normativa": "PGOU Boadilla"}',
    } in second_call_messages


def test_agent_raises_runtime_error_when_tool_is_not_registered():
    tool_calls = [{"id": "call_1", "name": "tool_desconocida", "arguments": "{}"}]
    fake_llm_service = FakeLlmService(
        response={"content": None, "tool_calls": tool_calls}
    )
    agent = Agent(
        llm_service=fake_llm_service,
        tools=[{"name": "tool_desconocida"}],
        tool_executors={},
    )

    with pytest.raises(RuntimeError):
        agent.ask("usa una tool desconocida")


def test_agent_raises_runtime_error_when_max_iterations_exceeded():
    tool_calls = [{"id": "call_1", "name": "buscar_normativa", "arguments": "{}"}]
    fake_llm_service = FakeLlmService(
        response={"content": None, "tool_calls": tool_calls}
    )
    agent = Agent(
        llm_service=fake_llm_service,
        tools=[{"name": "buscar_normativa"}],
        tool_executors={"buscar_normativa": lambda arguments: {"ok": True}},
        max_iterations=2,
    )

    with pytest.raises(RuntimeError):
        agent.ask("busca normativa indefinidamente")


def test_agent_keeps_conversation_history_between_turns():
    fake_llm_service = FakeLlmService(
        response={"content": "respuesta", "tool_calls": []}
    )
    agent = Agent(llm_service=fake_llm_service)

    agent.ask("primer mensaje")
    assert fake_llm_service.received_messages == [
        {"role": "user", "content": "primer mensaje"},
    ]

    agent.ask("segundo mensaje")
    assert fake_llm_service.received_messages == [
        {"role": "user", "content": "primer mensaje"},
        {"role": "assistant", "content": "respuesta"},
        {"role": "user", "content": "segundo mensaje"},
    ]

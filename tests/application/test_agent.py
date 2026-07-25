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


def test_agent_seeds_system_prompt_as_first_message():
    fake_llm_service = FakeLlmService(
        response={"content": "respuesta del asistente", "tool_calls": []}
    )
    agent = Agent(llm_service=fake_llm_service, system_prompt="eres un asistente")

    agent.ask("hola")

    assert fake_llm_service.received_messages[0] == {
        "role": "system",
        "content": "eres un asistente",
    }
    assert fake_llm_service.received_messages[1] == {
        "role": "user",
        "content": "hola",
    }


def test_agent_seeds_conversation_history_before_new_user_message():
    fake_llm_service = FakeLlmService(
        response={"content": "respuesta", "tool_calls": []}
    )
    agent = Agent(llm_service=fake_llm_service)

    agent.ask(
        "segunda pregunta",
        history=[
            {"role": "user", "content": "primera"},
            {"role": "assistant", "content": "respuesta previa"},
        ],
    )

    assert fake_llm_service.received_messages == [
        {"role": "user", "content": "primera"},
        {"role": "assistant", "content": "respuesta previa"},
        {"role": "user", "content": "segunda pregunta"},
    ]


def test_agent_forces_final_answer_without_tools_when_max_iterations_reached():
    tc = {"id": "call_1", "name": "buscar", "arguments": "{}"}
    fake_llm_service = FakeLlmService(
        responses=[
            {"content": None, "tool_calls": [tc]},
            {"content": None, "tool_calls": [tc]},
            {"content": "respuesta final con lo que tengo", "tool_calls": []},
        ]
    )
    agent = Agent(
        llm_service=fake_llm_service,
        tools=[{"name": "buscar"}],
        tool_executors={"buscar": lambda arguments: {"ok": True}},
        max_iterations=2,
        force_answer_on_max_iterations=True,
    )

    result = agent.ask("pregunta")

    assert result == "respuesta final con lo que tengo"
    assert fake_llm_service.received_tools is None


def test_agent_still_raises_on_max_iterations_when_force_answer_disabled():
    tool_calls = [{"id": "call_1", "name": "buscar_normativa", "arguments": "{}"}]
    fake_llm_service = FakeLlmService(
        response={"content": None, "tool_calls": tool_calls}
    )
    agent = Agent(
        llm_service=fake_llm_service,
        tools=[{"name": "buscar_normativa"}],
        tool_executors={"buscar_normativa": lambda arguments: {"ok": True}},
        max_iterations=2,
        force_answer_on_max_iterations=False,
    )

    with pytest.raises(RuntimeError):
        agent.ask("busca normativa indefinidamente")


def test_agent_prints_reasoning_of_each_round_when_present(capsys):
    tool_calls = [
        {"id": "call_1", "name": "buscar_normativa", "arguments": "{}"}
    ]
    fake_llm_service = FakeLlmService(
        responses=[
            {"content": "Voy a buscar la altura máxima aplicable", "tool_calls": tool_calls},
            {"content": "Con la normativa recuperada ya puedo responder", "tool_calls": []},
        ]
    )
    agent = Agent(
        llm_service=fake_llm_service,
        tools=[{"name": "buscar_normativa"}],
        tool_executors={"buscar_normativa": lambda arguments: {"ok": True}},
    )

    agent.ask("¿altura máxima?")

    output = capsys.readouterr().out
    assert "Ronda 1" in output
    assert "Voy a buscar la altura máxima aplicable" in output
    assert "Ronda 2" in output
    assert "Con la normativa recuperada ya puedo responder" in output


def test_agent_does_not_print_reasoning_when_content_is_empty(capsys):
    tool_calls = [
        {"id": "call_1", "name": "buscar_normativa", "arguments": "{}"}
    ]
    fake_llm_service = FakeLlmService(
        responses=[
            {"content": None, "tool_calls": tool_calls},
            {"content": "respuesta final", "tool_calls": []},
        ]
    )
    agent = Agent(
        llm_service=fake_llm_service,
        tools=[{"name": "buscar_normativa"}],
        tool_executors={"buscar_normativa": lambda arguments: {"ok": True}},
    )

    agent.ask("¿altura máxima?")

    output = capsys.readouterr().out
    assert "Ronda 1" not in output
    assert "respuesta final" in output


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

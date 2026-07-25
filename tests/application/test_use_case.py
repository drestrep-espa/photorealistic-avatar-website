from tests.fakes.fake_llm_service import FakeLlmService

from src.infrastructure.agent import Agent
from src.application.use_case import REVIEW_PROMPT, check_document_with_agent


def test_check_document_with_agent_sends_the_full_review_prompt_to_the_llm():
    fake_llm_service = FakeLlmService(
        response={"content": "respuesta del asistente", "tool_calls": []}
    )
    agent = Agent(llm_service=fake_llm_service)

    check_document_with_agent(agent)

    assert fake_llm_service.received_messages_per_call[0] == [
        {"role": "user", "content": REVIEW_PROMPT},
    ]


def test_review_prompt_is_not_empty_and_contains_key_instructions():
    assert REVIEW_PROMPT != ""
    assert "build_review_plan" in REVIEW_PROMPT
    assert "cumple_segun_datos_declarados" in REVIEW_PROMPT

from tests.fakes.fake_llm_service import FakeLlmService

from src.infrastructure.agent import Agent
from src.application.answer_normative_question import (
    NORMATIVE_QA_SYSTEM_PROMPT,
    answer_normative_question,
)


def test_normative_qa_system_prompt_is_not_empty_and_mentions_key_rules():
    assert NORMATIVE_QA_SYSTEM_PROMPT != ""
    assert "search_item" in NORMATIVE_QA_SYSTEM_PROMPT
    assert "4" in NORMATIVE_QA_SYSTEM_PROMPT
    assert "evidencia" in NORMATIVE_QA_SYSTEM_PROMPT


def test_answer_normative_question_returns_the_agent_answer():
    fake_llm_service = FakeLlmService(
        response={"content": "la altura máxima es 7 m", "tool_calls": []}
    )
    agent = Agent(llm_service=fake_llm_service, system_prompt=NORMATIVE_QA_SYSTEM_PROMPT)

    answer = answer_normative_question(agent=agent, question="¿altura máxima?")

    assert answer == "la altura máxima es 7 m"


def test_answer_normative_question_forwards_history_to_the_agent():
    fake_llm_service = FakeLlmService(
        response={"content": "en suelo urbano son 10 m", "tool_calls": []}
    )
    agent = Agent(llm_service=fake_llm_service, system_prompt=NORMATIVE_QA_SYSTEM_PROMPT)

    answer_normative_question(
        agent=agent,
        question="¿y en suelo urbano?",
        history=[
            {"role": "user", "content": "¿altura máxima?"},
            {"role": "assistant", "content": "7 m"},
        ],
    )

    contents = [message["content"] for message in fake_llm_service.received_messages]
    assert "¿altura máxima?" in contents
    assert "7 m" in contents
    assert "¿y en suelo urbano?" in contents
    assert contents.index("¿y en suelo urbano?") > contents.index("¿altura máxima?")
    assert contents.index("¿y en suelo urbano?") > contents.index("7 m")

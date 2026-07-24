import pytest

from src.domain.llm_cost_tracker import LlmCostTracker
from tests.fakes.fake_llm_cost_tracker import FakeLlmCostTracker


def test_llm_cost_tracker_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        LlmCostTracker()


def test_fake_llm_cost_tracker_summary_starts_empty():
    fake_llm_cost_tracker = FakeLlmCostTracker()

    result = fake_llm_cost_tracker.summary()

    assert result == {"entries": []}


def test_fake_llm_cost_tracker_record_registers_call_and_appears_in_summary():
    fake_llm_cost_tracker = FakeLlmCostTracker()

    fake_llm_cost_tracker.record(
        tool_name="build_review_plan",
        model="gpt-4.1",
        input_tokens=100,
        cached_input_tokens=20,
        output_tokens=50,
    )

    result = fake_llm_cost_tracker.summary()

    assert result == {
        "entries": [
            {
                "tool_name": "build_review_plan",
                "model": "gpt-4.1",
                "input_tokens": 100,
                "cached_input_tokens": 20,
                "output_tokens": 50,
            }
        ]
    }


def test_fake_llm_cost_tracker_record_accumulates_multiple_calls():
    fake_llm_cost_tracker = FakeLlmCostTracker()

    fake_llm_cost_tracker.record(
        tool_name="build_review_plan",
        model="gpt-4.1",
        input_tokens=100,
        cached_input_tokens=0,
        output_tokens=50,
    )
    fake_llm_cost_tracker.record(
        tool_name="agent_reasoning",
        model="gpt-4.1-mini",
        input_tokens=30,
        cached_input_tokens=10,
        output_tokens=15,
    )

    result = fake_llm_cost_tracker.summary()

    assert len(result["entries"]) == 2
    assert result["entries"][0]["tool_name"] == "build_review_plan"
    assert result["entries"][1]["tool_name"] == "agent_reasoning"

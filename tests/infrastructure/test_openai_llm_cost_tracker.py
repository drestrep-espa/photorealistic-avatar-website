import pytest

from src.domain.llm_cost_tracker import LlmCostTracker
from src.infrastructure.openai_llm_cost_tracker import OpenAiLlmCostTracker


def test_openai_llm_cost_tracker_inherits_from_llm_cost_tracker_port():
    tracker = OpenAiLlmCostTracker()

    assert isinstance(tracker, LlmCostTracker)


def test_record_calculates_standard_tier_cost_for_gpt_5_4():
    tracker = OpenAiLlmCostTracker()

    tracker.record(
        tool_name="build_review_plan",
        model="gpt-5.4",
        input_tokens=100_000,
        cached_input_tokens=0,
        output_tokens=100_000,
    )

    summary = tracker.summary()

    assert summary["total_cost_usd"] == pytest.approx(0.25 + 1.50)


def test_record_applies_cached_input_rate_for_gpt_5_4():
    tracker = OpenAiLlmCostTracker()

    tracker.record(
        tool_name="build_review_plan",
        model="gpt-5.4",
        input_tokens=100_000,
        cached_input_tokens=100_000,
        output_tokens=0,
    )

    summary = tracker.summary()

    assert summary["total_cost_usd"] == pytest.approx(0.025)


def test_record_switches_to_long_context_tier_when_total_tokens_exceed_threshold():
    tracker = OpenAiLlmCostTracker()

    tracker.record(
        tool_name="analyze_project",
        model="gpt-5.4",
        input_tokens=200_000,
        cached_input_tokens=0,
        output_tokens=100_000,
    )

    summary = tracker.summary()

    expected_cost = 200_000 / 1_000_000 * 5.00 + 100_000 / 1_000_000 * 22.50
    assert summary["total_cost_usd"] == pytest.approx(expected_cost)


def test_record_stays_in_standard_tier_when_total_tokens_at_threshold():
    tracker = OpenAiLlmCostTracker()

    tracker.record(
        tool_name="analyze_project",
        model="gpt-5.4",
        input_tokens=172_000,
        cached_input_tokens=0,
        output_tokens=100_000,
    )

    summary = tracker.summary()

    expected_cost = 172_000 / 1_000_000 * 2.50 + 100_000 / 1_000_000 * 15.00
    assert summary["total_cost_usd"] == pytest.approx(expected_cost)


def test_record_gpt_5_4_mini_always_uses_standard_tier_even_above_threshold():
    tracker = OpenAiLlmCostTracker()

    tracker.record(
        tool_name="analyze_project",
        model="gpt-5.4-mini",
        input_tokens=200_000,
        cached_input_tokens=0,
        output_tokens=100_000,
    )

    summary = tracker.summary()

    expected_cost = 200_000 / 1_000_000 * 0.75 + 100_000 / 1_000_000 * 4.50
    assert summary["total_cost_usd"] == pytest.approx(expected_cost)


def test_summary_starts_with_zero_cost_and_empty_breakdowns():
    tracker = OpenAiLlmCostTracker()

    summary = tracker.summary()

    assert summary["total_cost_usd"] == 0
    assert summary["by_tool"] == {}
    assert summary["by_model"] == {}


def test_summary_aggregates_multiple_calls_by_tool_and_model():
    tracker = OpenAiLlmCostTracker()

    tracker.record(
        tool_name="build_review_plan",
        model="gpt-5.4-mini",
        input_tokens=1_000,
        cached_input_tokens=200,
        output_tokens=500,
    )
    tracker.record(
        tool_name="build_review_plan",
        model="gpt-5.4-mini",
        input_tokens=2_000,
        cached_input_tokens=0,
        output_tokens=1_000,
    )
    tracker.record(
        tool_name="agent_reasoning",
        model="gpt-5.4",
        input_tokens=500,
        cached_input_tokens=0,
        output_tokens=100,
    )

    summary = tracker.summary()

    by_tool = summary["by_tool"]
    assert by_tool["build_review_plan"]["calls"] == 2
    assert by_tool["build_review_plan"]["input_tokens"] == 3_000
    assert by_tool["build_review_plan"]["cached_input_tokens"] == 200
    assert by_tool["build_review_plan"]["output_tokens"] == 1_500
    assert by_tool["agent_reasoning"]["calls"] == 1

    by_model = summary["by_model"]
    assert by_model["gpt-5.4-mini"]["calls"] == 2
    assert by_model["gpt-5.4"]["calls"] == 1

    expected_build_review_plan_cost = (
        (1_000 - 200) / 1_000_000 * 0.75
        + 200 / 1_000_000 * 0.075
        + 500 / 1_000_000 * 4.50
        + 2_000 / 1_000_000 * 0.75
        + 1_000 / 1_000_000 * 4.50
    )
    assert by_tool["build_review_plan"]["cost_usd"] == pytest.approx(
        expected_build_review_plan_cost
    )

    expected_total = expected_build_review_plan_cost + (
        500 / 1_000_000 * 2.50 + 100 / 1_000_000 * 15.00
    )
    assert summary["total_cost_usd"] == pytest.approx(expected_total)

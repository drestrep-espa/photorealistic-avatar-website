from typing import Any, Dict, List, Optional

from ..domain.llm_cost_tracker import LlmCostTracker

_LONG_CONTEXT_THRESHOLD_TOKENS = 272_000

_PRICING: Dict[str, Dict[str, Optional[Dict[str, float]]]] = {
    "gpt-5.4": {
        "standard": {"input": 2.50, "cached_input": 0.25, "output": 15.00},
        "long_context": {"input": 5.00, "cached_input": 0.50, "output": 22.50},
    },
    "gpt-5.4-mini": {
        "standard": {"input": 0.75, "cached_input": 0.075, "output": 4.50},
        "long_context": None,
    },
}


class OpenAiLlmCostTracker(LlmCostTracker):
    def __init__(self) -> None:
        self._entries: List[Dict[str, Any]] = []

    def record(
        self,
        *,
        tool_name: str,
        model: str,
        input_tokens: int,
        cached_input_tokens: int,
        output_tokens: int,
    ) -> None:
        cost_usd = self._calculate_cost(
            model=model,
            input_tokens=input_tokens,
            cached_input_tokens=cached_input_tokens,
            output_tokens=output_tokens,
        )
        self._entries.append(
            {
                "tool_name": tool_name,
                "model": model,
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
            }
        )

    def summary(self) -> Dict[str, Any]:
        total_cost_usd = sum(entry["cost_usd"] for entry in self._entries)
        return {
            "total_cost_usd": total_cost_usd,
            "by_tool": self._group_by(self._entries, "tool_name"),
            "by_model": self._group_by(self._entries, "model"),
        }

    def _calculate_cost(
        self,
        *,
        model: str,
        input_tokens: int,
        cached_input_tokens: int,
        output_tokens: int,
    ) -> float:
        model_pricing = _PRICING[model]
        tier = model_pricing["standard"]
        total_tokens = input_tokens + output_tokens
        long_context_pricing = model_pricing["long_context"]
        if total_tokens > _LONG_CONTEXT_THRESHOLD_TOKENS and long_context_pricing is not None:
            tier = long_context_pricing

        non_cached_input_tokens = input_tokens - cached_input_tokens
        return (
            non_cached_input_tokens / 1_000_000 * tier["input"]
            + cached_input_tokens / 1_000_000 * tier["cached_input"]
            + output_tokens / 1_000_000 * tier["output"]
        )

    def _group_by(self, entries: List[Dict[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
        grouped: Dict[str, Dict[str, Any]] = {}
        for entry in entries:
            group_key = entry[key]
            aggregate = grouped.setdefault(
                group_key,
                {
                    "cost_usd": 0.0,
                    "input_tokens": 0,
                    "cached_input_tokens": 0,
                    "output_tokens": 0,
                    "calls": 0,
                },
            )
            aggregate["cost_usd"] += entry["cost_usd"]
            aggregate["input_tokens"] += entry["input_tokens"]
            aggregate["cached_input_tokens"] += entry["cached_input_tokens"]
            aggregate["output_tokens"] += entry["output_tokens"]
            aggregate["calls"] += 1
        return grouped

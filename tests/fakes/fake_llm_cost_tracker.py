from typing import Any, Dict, List

from src.domain.llm_cost_tracker import LlmCostTracker


class FakeLlmCostTracker(LlmCostTracker):
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
        self._entries.append(
            {
                "tool_name": tool_name,
                "model": model,
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_input_tokens,
                "output_tokens": output_tokens,
            }
        )

    def summary(self) -> Dict[str, Any]:
        return {"entries": self._entries}

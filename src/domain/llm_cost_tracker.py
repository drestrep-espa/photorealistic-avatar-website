from abc import ABC, abstractmethod
from typing import Any, Dict


class LlmCostTracker(ABC):
    @abstractmethod
    def record(
        self,
        *,
        tool_name: str,
        model: str,
        input_tokens: int,
        cached_input_tokens: int,
        output_tokens: int,
    ) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        raise NotImplementedError  # pragma: no cover

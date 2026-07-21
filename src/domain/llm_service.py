from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LlmService(ABC):
    @abstractmethod
    def make_request(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        document_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError  # pragma: no cover

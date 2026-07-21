from typing import Any, Dict, List, Optional

from src.domain.normative_search_service import NormativeSearchService


class FakeNormativeSearchService(NormativeSearchService):
    def __init__(
        self,
        response: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self._response = response if response is not None else []
        self.received_query: Optional[str] = None
        self.received_max_results: Optional[int] = None

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        self.received_query = query
        self.received_max_results = max_results
        return self._response

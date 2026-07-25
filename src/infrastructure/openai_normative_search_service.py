from typing import Any, Dict, List, Optional

import openai

from ..domain.normative_search_service import NormativeSearchService


class OpenAiNormativeSearchService(NormativeSearchService):
    def __init__(
        self,
        api_key: str,
        vector_store_id: str,
        client: Optional[openai.OpenAI] = None,
    ) -> None:
        self._vector_store_id = vector_store_id
        self._client = client or openai.OpenAI(api_key=api_key)

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        response = self._client.vector_stores.search(
            vector_store_id=self._vector_store_id,
            query=query,
            max_num_results=max_results,
        )

        return [self._normalize_result(result) for result in response.data]

    def _normalize_result(self, result: Any) -> Dict[str, Any]:
        attributes = getattr(result, "attributes", None) or {}
        return {
            "text": self._extract_text(result),
            "score": getattr(result, "score", None),
            "filename": getattr(result, "filename", None),
            "page": attributes.get("page"),
        }

    def _extract_text(self, result: Any) -> str:
        content = getattr(result, "content", None) or []
        return "\n".join(content_part.text for content_part in content)

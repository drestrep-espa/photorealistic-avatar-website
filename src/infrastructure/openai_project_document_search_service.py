import os
from typing import Any, Dict, List, Optional

import openai

from ..domain.project_document_search_service import ProjectDocumentSearchService


class OpenAiProjectDocumentSearchService(ProjectDocumentSearchService):
    def __init__(
        self,
        api_key: str,
        vector_store_id: Optional[str] = None,
        client: Optional[openai.OpenAI] = None,
    ) -> None:
        self._client = client or openai.OpenAI(api_key=api_key)
        self._vector_store_id = vector_store_id

    def index_document(self, document_path: str) -> None:
        if self._vector_store_id is not None:
            self._delete_previous_index()

        with open(document_path, "rb") as document_file:
            file = self._client.files.create(file=document_file, purpose="assistants")

        vector_store = self._client.vector_stores.create(
            name=os.path.basename(document_path)
        )

        self._client.vector_stores.files.create_and_poll(
            vector_store_id=vector_store.id,
            file_id=file.id,
        )

        self._vector_store_id = vector_store.id

    def _delete_previous_index(self) -> None:
        files = self._client.vector_stores.files.list(
            vector_store_id=self._vector_store_id
        )
        for file in files:
            self._client.files.delete(file.id)

        self._client.vector_stores.delete(self._vector_store_id)

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

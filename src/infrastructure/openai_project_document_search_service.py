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

        print(f"[index] Subiendo '{document_path}' a OpenAI...", flush=True)
        with open(document_path, "rb") as document_file:
            file = self._client.files.create(file=document_file, purpose="assistants")
        print(f"[index] Fichero subido (file_id={file.id}).", flush=True)

        vector_store = self._client.vector_stores.create(
            name=os.path.basename(document_path)
        )
        print(
            f"[index] Vector store creado (id={vector_store.id}). "
            "Procesando el documento...",
            flush=True,
        )

        vector_store_file = self._client.vector_stores.files.create_and_poll(
            vector_store_id=vector_store.id,
            file_id=file.id,
        )
        status = getattr(vector_store_file, "status", "desconocido")
        print(
            f"[index] Proyecto indexado en vector store {vector_store.id} "
            f"(estado={status}).",
            flush=True,
        )

        self._vector_store_id = vector_store.id

    def delete_index(self) -> None:
        if self._vector_store_id is None:
            print("[cleanup] No hay vector store del proyecto que borrar.", flush=True)
            return

        print(
            f"[cleanup] Borrando vector store del proyecto {self._vector_store_id}...",
            flush=True,
        )
        self._delete_previous_index()
        self._vector_store_id = None
        print("[cleanup] Vector store del proyecto borrado.", flush=True)

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

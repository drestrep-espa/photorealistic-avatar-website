from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ProjectDocumentSearchService(ABC):
    @abstractmethod
    def index_document(self, document_path: str) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def delete_index(self) -> None:
        # Borra el vector store del proyecto actualmente indexado.
        # Debe ser seguro de llamar aunque no haya nada indexado.
        raise NotImplementedError  # pragma: no cover

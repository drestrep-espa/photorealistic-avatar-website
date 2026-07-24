from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ProjectDocumentSearchService(ABC):
    @abstractmethod
    def index_document(self, document_path: str) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError  # pragma: no cover

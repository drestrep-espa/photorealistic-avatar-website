from abc import ABC, abstractmethod


class TextExtractor(ABC):
    @abstractmethod
    def extract_text(self, document_path: str) -> str:
        raise NotImplementedError  # pragma: no cover

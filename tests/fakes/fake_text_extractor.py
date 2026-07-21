from typing import Optional

from src.domain.text_extractor import TextExtractor


class FakeTextExtractor(TextExtractor):
    def __init__(self, text: str = "texto por defecto") -> None:
        self._text = text
        self.received_document_path: Optional[str] = None

    def extract_text(self, document_path: str) -> str:
        self.received_document_path = document_path
        return self._text

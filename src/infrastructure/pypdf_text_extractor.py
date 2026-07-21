from pypdf import PdfReader

from ..domain.text_extractor import TextExtractor


class PyPdfTextExtractor(TextExtractor):
    def extract_text(self, document_path: str) -> str:
        reader = PdfReader(document_path)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text)

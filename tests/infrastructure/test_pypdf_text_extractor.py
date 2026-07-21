from fpdf import FPDF

from src.domain.text_extractor import TextExtractor
from src.infrastructure.pypdf_text_extractor import PyPdfTextExtractor

KNOWN_TEXT = "Memoria descriptiva del proyecto de prueba"


def _build_pdf_with_text(pdf_path: str, text: str) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text=text)
    pdf.output(pdf_path)


def test_extract_text_returns_known_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "memoria.pdf"
    _build_pdf_with_text(str(pdf_path), KNOWN_TEXT)

    extracted_text = PyPdfTextExtractor().extract_text(str(pdf_path))

    assert KNOWN_TEXT in extracted_text


def test_pypdf_text_extractor_is_a_text_extractor():
    extractor = PyPdfTextExtractor()

    assert isinstance(extractor, TextExtractor)

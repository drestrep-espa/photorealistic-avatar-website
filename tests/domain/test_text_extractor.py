import pytest

from src.domain.text_extractor import TextExtractor
from tests.fakes.fake_text_extractor import FakeTextExtractor


def test_text_extractor_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        TextExtractor()


def test_fake_text_extractor_extract_text_returns_configured_text():
    fake_text_extractor = FakeTextExtractor(text="texto extraido del pdf")

    result = fake_text_extractor.extract_text(document_path="/tmp/proyecto_basico.pdf")

    assert result == "texto extraido del pdf"
    assert fake_text_extractor.received_document_path == "/tmp/proyecto_basico.pdf"


def test_fake_text_extractor_extract_text_returns_default_text():
    fake_text_extractor = FakeTextExtractor()

    result = fake_text_extractor.extract_text(document_path="/tmp/otro_proyecto.pdf")

    assert result == "texto por defecto"
    assert fake_text_extractor.received_document_path == "/tmp/otro_proyecto.pdf"

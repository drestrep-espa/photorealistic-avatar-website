import pytest

from src.domain.normative_search_service import NormativeSearchService
from tests.fakes.fake_normative_search_service import FakeNormativeSearchService


def test_normative_search_service_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        NormativeSearchService()


def test_fake_normative_search_service_search_returns_default_empty_list():
    fake_normative_search_service = FakeNormativeSearchService()

    result = fake_normative_search_service.search(query="altura maxima Boadilla")

    assert result == []
    assert fake_normative_search_service.received_query == "altura maxima Boadilla"
    assert fake_normative_search_service.received_max_results == 5


def test_fake_normative_search_service_search_returns_configured_fragments():
    fragments = [
        {"text": "La altura maxima en zona R1 es de 7 metros", "score": 0.92, "filename": "pgou_boadilla.pdf"},
        {"text": "Retranqueo minimo a linderos: 3 metros", "score": None, "filename": None},
    ]
    fake_normative_search_service = FakeNormativeSearchService(response=fragments)

    result = fake_normative_search_service.search(query="retranqueo", max_results=2)

    assert result == fragments
    assert fake_normative_search_service.received_query == "retranqueo"
    assert fake_normative_search_service.received_max_results == 2

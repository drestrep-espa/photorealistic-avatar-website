from tests.fakes.fake_normative_search_service import FakeNormativeSearchService

from src.application.search_item import search_item


def _fragments():
    return [
        {"text": "Altura máxima 7 metros y 2 plantas", "score": 0.91, "filename": "PGOU.pdf"},
        {"text": "Retranqueo mínimo a linderos 3 metros", "score": 0.85, "filename": "PGOU.pdf"},
    ]


def test_search_item_returns_fragments_from_normative_search_service():
    fake_normative_search_service = FakeNormativeSearchService(response=_fragments())

    result = search_item(
        normative_search_service=fake_normative_search_service,
        query="altura máxima unifamiliar aislada",
    )

    assert result == _fragments()


def test_search_item_passes_query_and_max_results_to_the_port():
    fake_normative_search_service = FakeNormativeSearchService(response=_fragments())

    search_item(
        normative_search_service=fake_normative_search_service,
        query="retranqueos a lindero",
        max_results=3,
    )

    assert fake_normative_search_service.received_query == "retranqueos a lindero"
    assert fake_normative_search_service.received_max_results == 3


def test_search_item_uses_default_max_results_when_not_provided():
    fake_normative_search_service = FakeNormativeSearchService(response=_fragments())

    search_item(
        normative_search_service=fake_normative_search_service,
        query="edificabilidad máxima",
    )

    assert fake_normative_search_service.received_max_results == 8

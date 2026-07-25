import pytest

from src.domain.report_generator import ReportGenerator
from tests.fakes.fake_report_generator import FakeReportGenerator


def test_report_generator_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        ReportGenerator()


def test_fake_report_generator_generate_stores_received_arguments():
    fake_report_generator = FakeReportGenerator()

    result = fake_report_generator.generate(
        content="Informe de revision del proyecto basico", output_dir="/tmp/informes"
    )

    assert result == "data/informe/informe_fake.pdf"
    assert fake_report_generator.received_content == "Informe de revision del proyecto basico"
    assert fake_report_generator.received_output_dir == "/tmp/informes"


def test_fake_report_generator_returns_configured_output_path():
    fake_report_generator = FakeReportGenerator(output_path="/tmp/informes/informe_custom.pdf")

    result = fake_report_generator.generate(content="contenido", output_dir="/tmp/informes")

    assert result == "/tmp/informes/informe_custom.pdf"

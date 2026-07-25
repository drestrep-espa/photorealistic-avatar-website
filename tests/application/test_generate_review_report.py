from tests.fakes.fake_report_generator import FakeReportGenerator

from src.application.generate_review_report import generate_review_report


def test_generate_review_report_sends_content_and_output_dir_to_the_port():
    fake_report_generator = FakeReportGenerator()

    generate_review_report(
        report_generator=fake_report_generator,
        content="Informe de revision del proyecto basico",
        output_dir="/tmp/informes",
    )

    assert (
        fake_report_generator.received_content
        == "Informe de revision del proyecto basico"
    )
    assert fake_report_generator.received_output_dir == "/tmp/informes"


def test_generate_review_report_returns_the_generated_report_path():
    fake_report_generator = FakeReportGenerator(
        output_path="data/informe/informe_final.pdf"
    )

    result = generate_review_report(
        report_generator=fake_report_generator,
        content="contenido",
        output_dir="/tmp/informes",
    )

    assert result == "data/informe/informe_final.pdf"

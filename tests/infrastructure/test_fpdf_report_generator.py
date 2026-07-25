from unittest.mock import MagicMock, patch

from src.domain.report_generator import ReportGenerator
from src.infrastructure.fpdf_report_generator import FpdfReportGenerator

MODULE = "src.infrastructure.fpdf_report_generator"


def _build_fake_fpdf() -> MagicMock:
    return MagicMock()


def test_generate_writes_pdf_and_returns_its_path():
    fake_pdf_instance = _build_fake_fpdf()
    with patch(f"{MODULE}.FPDF", return_value=fake_pdf_instance), patch(
        f"{MODULE}.os.makedirs"
    ):
        result_path = FpdfReportGenerator().generate(
            content="Informe de prueba", output_dir="data/informe"
        )

    fake_pdf_instance.output.assert_called_once()
    (output_call_arg,), _ = fake_pdf_instance.output.call_args
    assert output_call_arg.startswith("data/informe")
    assert output_call_arg.endswith(".pdf")
    assert result_path == output_call_arg


def test_generate_calls_add_page_set_font_and_multi_cell():
    fake_pdf_instance = _build_fake_fpdf()
    with patch(f"{MODULE}.FPDF", return_value=fake_pdf_instance), patch(
        f"{MODULE}.os.makedirs"
    ):
        FpdfReportGenerator().generate(content="Informe de prueba", output_dir="data/informe")

    fake_pdf_instance.add_page.assert_called_once()
    assert fake_pdf_instance.set_font.call_count >= 1
    assert fake_pdf_instance.multi_cell.call_count >= 1


def test_generate_creates_output_dir_when_missing():
    fake_pdf_instance = _build_fake_fpdf()
    with patch(f"{MODULE}.FPDF", return_value=fake_pdf_instance), patch(
        f"{MODULE}.os.makedirs"
    ) as fake_makedirs:
        FpdfReportGenerator().generate(content="Informe de prueba", output_dir="data/informe")

    fake_makedirs.assert_called_once_with("data/informe", exist_ok=True)


def test_fpdf_report_generator_inherits_from_port():
    with patch(f"{MODULE}.FPDF"), patch(f"{MODULE}.os.makedirs"):
        service = FpdfReportGenerator()

    assert isinstance(service, ReportGenerator)

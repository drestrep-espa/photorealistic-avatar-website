from typing import Optional

from src.domain.report_generator import ReportGenerator


class FakeReportGenerator(ReportGenerator):
    def __init__(self, output_path: str = "data/informe/informe_fake.pdf") -> None:
        self._output_path = output_path
        self.received_content: Optional[str] = None
        self.received_output_dir: Optional[str] = None

    def generate(self, content: str, output_dir: str) -> str:
        self.received_content = content
        self.received_output_dir = output_dir
        return self._output_path

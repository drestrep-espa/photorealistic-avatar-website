from ..domain.report_generator import ReportGenerator


def generate_review_report(
    *, report_generator: ReportGenerator, content: str, output_dir: str
) -> str:
    return report_generator.generate(content, output_dir)

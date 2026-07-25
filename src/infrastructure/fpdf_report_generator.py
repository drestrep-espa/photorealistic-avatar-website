import os
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from ..domain.report_generator import ReportGenerator

FONT_REGULAR_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class FpdfReportGenerator(ReportGenerator):
    def generate(self, content: str, output_dir: str) -> str:
        os.makedirs(output_dir, exist_ok=True)

        pdf = FPDF()
        pdf.add_font("DejaVu", "", FONT_REGULAR_PATH)
        pdf.add_font("DejaVu", "B", FONT_BOLD_PATH)
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.multi_cell(
            0,
            8,
            "Informe de pre-revisión del proyecto",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(
            0,
            5,
            datetime.now().strftime("Generado el %Y-%m-%d %H:%M:%S"),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        pdf.ln(4)
        pdf.set_font("DejaVu", "", 11)
        pdf.multi_cell(0, 6, content or "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        filename = f"informe_revision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, filename)
        pdf.output(output_path)

        return output_path

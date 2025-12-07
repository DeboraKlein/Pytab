"""
pytab.reports.pdf_report
------------------------
Geração de relatórios executivos e técnicos em PDF.

Versão 0.1.0:
- Estrutura inicial
- Exporta PDF simples com título

Versões futuras:
- Inserir gráficos
- Inserir análise automática
- Templates executivos e técnicos
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_simple_report(path: str, title: str = "PyTab Report"):
    c = canvas.Canvas(path, pagesize=A4)

    # caminho do logo relativo a este arquivo
    logo_path = Path(__file__).parent.parent.parent / "docs" / "assets" / "Pytab_logoPDF.svg"

    # desenha o logo no topo
    if logo_path.exists():
        c.drawImage(str(logo_path), x=50, y=750, width=120, height=40, preserveAspectRatio=True, mask="auto")

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 720, title)

    c.showPage()
    c.save()
    return path

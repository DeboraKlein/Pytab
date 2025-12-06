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

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_simple_report(path: str, title: str = "PyTab Report"):
    """
    Gera um PDF simples com um título.
    """

    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 780, title)
    c.showPage()
    c.save()

    return path

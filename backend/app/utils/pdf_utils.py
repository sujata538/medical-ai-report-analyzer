"""
PDF generation utilities.

Generates a downloadable PDF version of an analyzed report (summary,
parameters table, recommendations, disclaimer) using ReportLab, so users
can save/print/share their results outside the app.

Requires: `pip install reportlab`.
"""
from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)


def generate_report_pdf(report) -> bytes:
    """
    Builds a simple, readable PDF summarizing a Report ORM object.
    Returns raw PDF bytes suitable for a StreamingResponse.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
    except ImportError as exc:
        raise RuntimeError("reportlab is not installed. Run: pip install reportlab") from exc

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Lab Report Summary — {report.title}", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Health Score: {report.health_score} / 100 ({report.risk_category})", styles["Heading2"]))
    story.append(Spacer(1, 8))

    if report.ai_summary:
        story.append(Paragraph("Summary", styles["Heading3"]))
        for line in report.ai_summary.split("\n"):
            story.append(Paragraph(line or "&nbsp;", styles["Normal"]))
        story.append(Spacer(1, 12))

    if report.parameters:
        story.append(Paragraph("Extracted Parameters", styles["Heading3"]))
        data = [["Parameter", "Value", "Unit", "Flag"]]
        for p in report.parameters:
            data.append([p.name, str(p.value), p.unit or "-", p.flag.value.replace("_", " ")])
        table = Table(data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 12))

    story.append(Paragraph(
        "This application is intended only for educational and informational purposes and "
        "is NOT a substitute for professional medical advice, diagnosis, or treatment.",
        styles["Italic"],
    ))

    doc.build(story)
    return buffer.getvalue()

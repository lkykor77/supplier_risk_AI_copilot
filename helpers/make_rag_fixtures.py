"""Generate the two public fictional evidence PDFs (requires reportlab)."""

import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path(__file__).resolve().parents[1]
fixture = json.loads((ROOT / "examples/rag/fixture.json").read_text())
styles = getSampleStyleSheet()
styles["BodyText"].fontSize = 11
styles["BodyText"].leading = 17
for document in fixture["documents"]:
    story = []
    for i, page in enumerate(document["pages"]):
        if i:
            story.append(PageBreak())
        story += [
            Paragraph(
                "SUPPLIER SECURITY EVIDENCE | FICTIONAL TRAINING SAMPLE",
                styles["Heading3"],
            ),
            Spacer(1, 18),
            Paragraph(fixture["supplier"], styles["Title"]),
            Spacer(1, 16),
            Paragraph(page["title"], styles["Heading2"]),
            Spacer(1, 12),
            Paragraph(page["text"], styles["BodyText"]),
            Spacer(1, 24),
            Paragraph(
                "Development fixture. Statements may conflict across documents. Human review is required; no certification or verified compliance is claimed.",
                styles["Italic"],
            ),
        ]

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#466057"))
        canvas.drawString(48, 34, "Fictional Supplier L | Local RAG evidence pack")
        canvas.drawRightString(548, 34, "Page " + str(doc.page))

    SimpleDocTemplate(
        str(ROOT / "examples/rag" / document["filename"]),
        title=fixture["supplier"] + " - " + document["filename"],
        author="Portfolio training fixture",
        leftMargin=48,
        rightMargin=48,
        topMargin=48,
        bottomMargin=58,
    ).build(story, onFirstPage=footer, onLaterPages=footer)

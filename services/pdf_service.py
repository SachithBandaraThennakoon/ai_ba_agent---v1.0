from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from datetime import datetime
import os
import re


# -------------------------------
# Markdown → ReportLab converter
# -------------------------------
def md_to_rl(text: str) -> str:
    """
    Convert basic Markdown to ReportLab-compatible markup
    """
    # Bold **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    # Italic *text*
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)

    return text


# -------------------------------
# Main PDF generator
# -------------------------------
def markdown_to_pdf(markdown_text: str, prefix: str = "Xceed_Proposal") -> str:
    folder = "proposals"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.pdf"
    filepath = os.path.join(folder, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(
        ParagraphStyle(
            name="ProposalTitle",
            fontSize=18,
            leading=22,
            spaceAfter=20,
            alignment=TA_LEFT,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Heading",
            fontSize=14,
            leading=18,
            spaceBefore=18,
            spaceAfter=10,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Body",
            fontSize=10.5,
            leading=14,
            spaceAfter=8,
        )
    )

    story = []
    bullet_buffer = []

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            story.append(
                ListFlowable(
                    [
                        ListItem(
                            Paragraph(md_to_rl(b), styles["Body"])
                        )
                        for b in bullet_buffer
                    ],
                    bulletType="bullet",
                    start="•",
                    leftIndent=18,
                )
            )
            story.append(Spacer(1, 8))
            bullet_buffer = []

    lines = markdown_text.split("\n")

    for line in lines:
        line = line.strip()

        # Empty line
        if not line:
            flush_bullets()
            story.append(Spacer(1, 10))
            continue

        # Headings (#, ##)
        if line.startswith("#"):
            flush_bullets()
            level = line.count("#")
            text = line.replace("#", "").strip()

            if level == 1:
                story.append(Paragraph(md_to_rl(text), styles["ProposalTitle"]))
            else:
                story.append(Paragraph(md_to_rl(text), styles["Heading"]))
            continue

        # Bullet points (- or *)
        if line.startswith("- ") or line.startswith("* "):
            bullet_buffer.append(line[2:].strip())
            continue

        # Normal paragraph
        flush_bullets()
        story.append(Paragraph(md_to_rl(line), styles["Body"]))

    flush_bullets()
    doc.build(story)

    return filepath

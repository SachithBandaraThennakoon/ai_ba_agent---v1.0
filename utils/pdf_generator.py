from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os

def markdown_to_pdf(markdown_text: str, prefix: str = "final_proposal") -> str:
    folder = "proposals"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.pdf"
    filepath = os.path.join(folder, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for line in markdown_text.split("\n"):
        line = line.strip()

        if not line:
            story.append(Spacer(1, 10))
            continue

        # Headings
        if line.startswith("#"):
            level = line.count("#")
            text = line.replace("#", "").strip()
            style = styles["Heading1"] if level == 1 else styles["Heading2"]
            story.append(Paragraph(text, style))
        else:
            story.append(Paragraph(line, styles["BodyText"]))

        story.append(Spacer(1, 8))

    doc.build(story)
    return filepath

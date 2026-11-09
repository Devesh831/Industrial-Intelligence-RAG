"""Make fictional PDFs for testing; never use these as operating instructions."""
from pathlib import Path
from reportlab.pdfgen import canvas

DOCS = Path(__file__).parent / "demo_docs"
EXAMPLES = {
    "fictional_draft_guide.pdf": ["FICTIONAL TEST DOCUMENT - NOT OPERATING INSTRUCTIONS", "For this fictional training example, a sudden draft drop can coincide with a fan interruption or a blocked duct. An operator should verify the sensor reading and check the fan and duct."],
    "fictional_temperature_guide.pdf": ["FICTIONAL TEST DOCUMENT - NOT OPERATING INSTRUCTIONS", "In this fictional example, an inlet temperature increase can coincide with a change in heat input. Confirm the temperature sensor and inspect the heating system before drawing conclusions."],
}
DOCS.mkdir(exist_ok=True)
for filename, lines in EXAMPLES.items():
    c = canvas.Canvas(str(DOCS / filename)); text = c.beginText(54, 760); text.setFont("Helvetica", 11)
    for line in lines:
        import textwrap
        for part in textwrap.wrap(line, 90): text.textLine(part)
        text.textLine("")
    c.drawText(text); c.save()

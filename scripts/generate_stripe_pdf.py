# requirements: pip install reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_stripe_guidelines():
    doc = SimpleDocTemplate("Stripe_Brand_Guidelines.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # --- Custom Styles ---
    title_style = ParagraphStyle(
        'StripeTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#0A2540"),  # Stripe 'Downriver'
        spaceAfter=20
    )

    h2_style = ParagraphStyle(
        'StripeH2',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor("#635BFF"),  # Stripe 'Blurple'
        spaceBefore=15,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        'StripeBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#425466")  # Stripe Slate
    )

    # --- TITLE PAGE ---
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Stripe Identity System", title_style))
    story.append(Paragraph("Version 4.2 | Internal Usage Only", body_style))
    story.append(PageBreak())

    # --- SECTION 1: IDENTITY CORE ---
    story.append(Paragraph("1. Identity Core", title_style))
    story.append(Paragraph("Archetype: The Sage / The Ruler", h2_style))
    story.append(Paragraph(
        """Stripe facilitates the internet economy. Our archetype is a blend of <b>The Sage</b> 
        (driven by knowledge, truth, and clarity) and <b>The Ruler</b> (creating structure, 
        stability, and order). We are never chaotic; we are the infrastructure.""",
        body_style
    ))

    story.append(Paragraph("Voice Vectors", h2_style))
    data = [
        ["Dimension", "Score (0.0 - 1.0)", "Note"],
        ["Formal vs. Casual", "0.7", "Professional but accessible."],
        ["Technical vs. Marketing", "0.6", "Precise, but plain-spoken."],
        ["Enthusiastic vs. Matter-of-fact", "0.3", "Calm confidence. No exclamation marks."],
    ]
    t = Table(data, colWidths=[2*inch, 1.5*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F6F9FC")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0A2540")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E6E6E6")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))

    # --- SECTION 2: VISUAL TOKENS ---
    story.append(Paragraph("2. Visual Tokens", title_style))
    story.append(Paragraph("Primary Palette", h2_style))
    story.append(Paragraph(
        "These colors define the core Stripe brand. Precision is mandatory.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))

    color_data = [
        ["Name", "Hex", "Role", "Sample"],
        ["Blurple", "#635BFF", "Primary Accent / Buttons", ""],
        ["Downriver", "#0A2540", "Text / Headings", ""],
        ["Slate", "#425466", "Body Text", ""],
        ["White", "#FFFFFF", "Backgrounds", ""],
        ["Black Squeeze", "#F6F9FC", "Secondary Background", ""],
    ]
    t_colors = Table(color_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1*inch])
    t_colors.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F6F9FC")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E6E6E6")),
        ('BACKGROUND', (3,1), (3,1), colors.HexColor("#635BFF")),  # Blurple
        ('BACKGROUND', (3,2), (3,2), colors.HexColor("#0A2540")),  # Downriver
        ('BACKGROUND', (3,3), (3,3), colors.HexColor("#425466")),  # Slate
        ('BACKGROUND', (3,4), (3,4), colors.HexColor("#FFFFFF")),  # White
        ('BACKGROUND', (3,5), (3,5), colors.HexColor("#F6F9FC")),  # Black Squeeze
    ]))
    story.append(t_colors)

    story.append(Paragraph("Typography", h2_style))
    story.append(Paragraph(
        """<b>Primary Font:</b> Ideal Sans (Proprietary). <br/>
        <b>Fallback Font:</b> Inter or System UI. <br/>
        <b>Usage:</b> Headings must use tight letter-spacing (-0.02em). 
        Body copy should be legible with generous line height (1.5).""",
        body_style
    ))

    # --- SECTION 3: GOVERNANCE RULES ---
    story.append(Paragraph("3. Governance Rules", title_style))
    rules = [
        ("G-01", "Contrast", "Text on 'Blurple' backgrounds must always be White (#FFFFFF). Never use Slate text on Blurple."),
        ("G-02", "Logo Space", "The 'Stripe' wordmark must have clear space equal to 150% of the height of the letter 'S'."),
        ("G-03", "Terminology", "Never use the word 'cost'. Use 'pricing' or 'fees'."),
        ("G-04", "Imagery", "Abstract geometric shapes (The 'S' ribbon) are preferred over stock photography. Human subjects should look candid, not posed."),
        ("G-05", "Gradients", "Gradients should be subtle (10-15% opacity change) and move from top-left to bottom-right."),
    ]

    for rid, title, text in rules:
        story.append(Paragraph(f"<b>[{rid}] {title}:</b> {text}", body_style))
        story.append(Spacer(1, 0.1*inch))

    doc.build(story)
    print("✅ PDF generated: Stripe_Brand_Guidelines.pdf")

if __name__ == "__main__":
    create_stripe_guidelines()

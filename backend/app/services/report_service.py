import io
import os
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def generate_pdf_report(user, features, prediction, sessions_summary):
    os.makedirs(REPORTS_DIR, exist_ok=True)

    filename = f"report_{user.id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=18, spaceAfter=12)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=14, spaceAfter=8)
    body_style = styles["Normal"]
    disclaimer_style = ParagraphStyle(
        "Disclaimer", parent=styles["Normal"], fontSize=9, textColor=colors.red
    )

    story = []

    story.append(Paragraph("Motor Asymmetry Decision-Support Report", title_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            "<b>DISCLAIMER:</b> This report contains exploratory digital biomarker data only. "
            "It does NOT constitute a medical diagnosis. All findings must be reviewed by a "
            "qualified neurologist.",
            disclaimer_style,
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Patient Information", heading_style))
    patient_data = [
        ["Name", user.full_name],
        ["Age", str(user.age)],
        ["Handedness", user.handedness.title()],
        ["Report Date", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")],
    ]
    t = Table(patient_data, colWidths=[5 * cm, 10 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Risk Assessment Summary", heading_style))
    risk_data = [
        ["Risk Profile", prediction["risk_profile"].upper()],
        ["Confidence", f"{prediction['confidence'] * 100:.1f}%"],
        ["Recommendation", prediction["recommendation"]],
    ]
    t = Table(risk_data, colWidths=[5 * cm, 10 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Longitudinal Biomarker Features", heading_style))
    feat_rows = [["Feature", "Value"]]
    for key, val in features.items():
        feat_rows.append([key.replace("_", " ").title(), f"{val:.3f}" if isinstance(val, float) else str(val)])
    t = Table(feat_rows, colWidths=[8 * cm, 7 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Session History Summary", heading_style))
    story.append(
        Paragraph(
            f"Total sessions: {sessions_summary.get('total_sessions', 0)} | "
            f"Assessment period: {sessions_summary.get('period', 'N/A')}",
            body_style,
        )
    )
    story.append(Spacer(1, 1 * cm))

    story.append(
        Paragraph(
            "<b>For the attending neurologist:</b> This report summarizes gamified motor "
            "assessment data (Reaction Time, Flight Time, Hold Time, Directional Asymmetry) "
            "collected via mobile micro-tasks over a longitudinal period. Trends should be "
            "interpreted alongside clinical examination.",
            body_style,
        )
    )

    doc.build(story)
    return filepath

"""
report_generator.py
-------------------
Official Clinical Diagnostic Report Generator for RadiVision AI.
Renders pixel-perfect, RSNA-compliant radiology reports with:
- Top rounded capsule badge: "RADIVERSION AI — Diagnostic Imaging Report"
- 1. PATIENT INFORMATION structured demographics table
- 2. Centered radiographic imaging viewport with Grad-CAM and bounding box
- 3. DIAGNOSTIC IMPRESSION with bold clinical color tagging
- 4. LOCAL HEALTHCARE & SPECIALIST REFERRALS with GPS-matched hospitals and doctors
- Clean, empty bottom margin with zero clutter
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from PIL import Image

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
    from reportlab.graphics.shapes import Drawing, Rect, String
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from app.hospital_referral import get_recommended_facilities

def generate_pdf_report(scan_details: Dict[str, Any]) -> str:
    """
    Generates a professional clinical diagnostic PDF report matching the exact
    RadiVision AI clinical specification.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    scan_id = scan_details.get("scan_id", "TEMP")
    patient_id = scan_details.get("patient_id", "RV-987654")
    filename = f"report_{patient_id}_{scan_id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)

    if not HAS_REPORTLAB:
        txt_path = pdf_path.replace(".pdf", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"RADIVERSION AI — Diagnostic Imaging Report\n\n")
            f.write(f"Patient: {scan_details.get('patient_name')} | Age: {scan_details.get('patient_age')}\n")
            f.write(f"Diagnosis: {scan_details.get('prediction')}\n")
        return txt_path

    # Build PDF with clean margins
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()
    story = []

    # 1. Top Capsule Shape Badge
    # Width ~400pt, height 36pt, rounded corners
    d = Drawing(532, 42)
    capsule_w = 420
    capsule_h = 32
    capsule_x = (532 - capsule_w) / 2
    capsule_y = 5

    # Dark blue capsule
    d.add(Rect(
        capsule_x, capsule_y, capsule_w, capsule_h,
        rx=16, ry=16,
        fillColor=colors.HexColor("#0B3D66"),
        strokeColor=None
    ))
    # Centered white bold text
    d.add(String(
        266, capsule_y + 10,
        "RADIVERSION AI — Diagnostic Imaging Report",
        fontName="Helvetica-Bold",
        fontSize=12.5,
        textAnchor="middle",
        fillColor=colors.white
    ))
    story.append(d)
    story.append(Spacer(1, 14))

    # Section Heading Style
    sec_heading_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=6
    )

    # 2. Section 1: PATIENT INFORMATION
    story.append(Paragraph("<b>1. PATIENT INFORMATION</b>", sec_heading_style))

    p_name = scan_details.get("patient_name", "Sarah Chen")
    p_age = str(scan_details.get("patient_age", "34"))
    p_id = str(scan_details.get("patient_id", "RV-987654"))
    date_str = scan_details.get("date", datetime.now().strftime("%d %b %Y"))
    modality = scan_details.get("scan_type", "Bone Radiograph (Wrist)")
    if "region" in scan_details and scan_details["region"]:
        modality = f"{modality} ({scan_details['region']})"
    location_str = scan_details.get("location", "New York")

    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor("#2D3748"))
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor("#1A202C"))

    demographics_data = [
        [
            Paragraph("<b>Patient Name:</b>", cell_bold), Paragraph(p_name, cell_style),
            Paragraph("<b>Age:</b>", cell_bold), Paragraph(p_age, cell_style)
        ],
        [
            Paragraph("<b>Patient ID:</b>", cell_bold), Paragraph(p_id, cell_style),
            Paragraph("<b>Date:</b>", cell_bold), Paragraph(date_str, cell_style)
        ],
        [
            Paragraph("<b>Modality:</b>", cell_bold), Paragraph(modality, cell_style),
            Paragraph("<b>Location:</b>", cell_bold), Paragraph(location_str, cell_style)
        ]
    ]

    t_demo = Table(demographics_data, colWidths=[95, 171, 75, 191])
    t_demo.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#A0AEC0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F7FAFC")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#F7FAFC")),
    ]))
    story.append(t_demo)
    story.append(Spacer(1, 12))

    # 3. Section 2: Radiographic Localization
    story.append(Paragraph("<b>2.</b>", sec_heading_style))

    image_path = scan_details.get("annotated_image_path") or scan_details.get("image_path")
    if image_path and os.path.exists(image_path):
        try:
            with Image.open(image_path) as im:
                w, h = im.size
                max_w = 260
                max_h = 210
                ratio = min(max_w / w, max_h / h)
                display_w = w * ratio
                display_h = h * ratio

            rl_img = RLImage(image_path, width=display_w, height=display_h)
            img_table = Table([[rl_img]], colWidths=[532])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(img_table)
        except Exception as e:
            print(f"[PDF Generator] Could not embed radiograph: {e}")
            story.append(Spacer(1, 150))
    else:
        story.append(Spacer(1, 150))

    story.append(Spacer(1, 10))

    # 4. Section 3: DIAGNOSTIC IMPRESSION
    story.append(Paragraph("<b>3. DIAGNOSTIC IMPRESSION</b>", sec_heading_style))

    prediction = scan_details.get("prediction", "Distal Radius Cortical Fracture")
    conf_val = scan_details.get("confidence", 0.984)
    if conf_val < 1.0:
        conf_str = f"{conf_val * 100:.1f}%"
    else:
        conf_str = f"{conf_val:.1f}%"

    is_abnormal = "abnormal" in prediction.lower() or "fracture" in prediction.lower() or "pneumonia" in prediction.lower()
    highlight_color = "#C53030" if is_abnormal else "#276749"  # Red for abnormal, green for normal

    impression_style = ParagraphStyle(
        'ImpressionText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor(highlight_color),
        spaceAfter=12
    )

    impression_line = f"{prediction} ({conf_str} Confidence)"
    story.append(Paragraph(impression_line, impression_style))

    # 5. Section 4: LOCAL HEALTHCARE & SPECIALIST REFERRALS
    story.append(Paragraph("<b>4. LOCAL HEALTHCARE & SPECIALIST REFERRALS</b>", sec_heading_style))

    facilities = get_recommended_facilities(location_str, modality, is_abnormal)
    referral_rows = []
    
    ref_title_style = ParagraphStyle('RefTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#1A202C"))
    ref_val_style = ParagraphStyle('RefVal', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#2D3748"))

    for f_idx, fac in enumerate(facilities):
        referral_rows.append([
            Paragraph(f"<b>Hospital:</b> {fac.get('hospital')}", ref_title_style)
        ])
        referral_rows.append([
            Paragraph(f"<b>Doctor:</b> {fac.get('doctor')}", ref_val_style)
        ])
        referral_rows.append([
            Paragraph(f"<b>Phone No:</b> {fac.get('phone')}", ref_val_style)
        ])
        if f_idx < len(facilities) - 1:
            referral_rows.append([Spacer(1, 5)])

    t_referral = Table(referral_rows, colWidths=[510])
    t_referral.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EBF8FF")), # Soft light blue
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BEE3F8")),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    story.append(t_referral)

    # Clean bottom margin - no footer logos or signatures
    doc.build(story)
    print(f"[PDF Generator] Successfully compiled clinical report: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    # Test generation with sample details
    sample = {
        "patient_name": "Sarah Chen",
        "patient_age": 34,
        "patient_id": "RV-987654",
        "date": "12 Oct 2026",
        "scan_type": "Bone Radiograph",
        "region": "Wrist",
        "location": "New York",
        "prediction": "Distal Radius Cortical Fracture",
        "confidence": 0.984,
        "image_path": r"d:\My Projects\RadiVision AI\model\bone\confusion_matrix.png"
    }
    generate_pdf_report(sample)

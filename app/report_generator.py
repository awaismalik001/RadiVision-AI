"""
report_generator.py
-------------------
Clinical PDF Diagnostic Report Generator for RadiVision AI.
Compiles patient demographics, original radiographs, OpenCV annotated findings,
and structured findings tables into an exportable PDF using ReportLab.
"""

import os
from datetime import datetime
from typing import Dict, Any, List

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

def generate_pdf_report(scan_details: Dict[str, Any]) -> str:
    """
    Generates a clinical diagnostic PDF report from scan details.
    Returns the absolute path to the generated PDF.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    scan_id = scan_details.get("scan_id", "TEMP")
    patient_id = scan_details.get("patient_id", "0")
    filename = f"report_patient_{patient_id}_scan_{scan_id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)

    if not HAS_REPORTLAB:
        # Simple plain-text fallback if ReportLab is not installed
        txt_path = pdf_path.replace(".pdf", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("     RADIVISION AI - CLINICAL DIAGNOSTIC REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Patient Name : {scan_details.get('patient_name')}\n")
            f.write(f"Patient Age  : {scan_details.get('patient_age')} | Gender: {scan_details.get('patient_gender')}\n")
            f.write(f"Scan Type    : {scan_details.get('scan_type')} | Region: {scan_details.get('body_region')}\n")
            f.write(f"Primary Diag : {scan_details.get('prediction')} ({scan_details.get('confidence', 0)*100:.1f}%)\n\n")
            f.write("FINDINGS:\n")
            for idx, finding in enumerate(scan_details.get("findings", []), 1):
                f.write(f"  {idx}. {finding.get('label')} (Confidence: {finding.get('confidence', 0)*100:.1f}%)\n")
        return txt_path

    # Build PDF with ReportLab
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    style_inst = ParagraphStyle(
        'InstitutionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=colors.HexColor("#0B3D66"),
        spaceAfter=2,
        alignment=1 # Center
    )

    style_sub = ParagraphStyle(
        'DepartmentSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#718096"),
        spaceAfter=12,
        alignment=1
    )

    style_title = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor("#14507D"),
        spaceAfter=10,
        alignment=1
    )

    style_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor("#0B3D66"),
        spaceBefore=10,
        spaceAfter=6
    )

    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#1A202C")
    )

    style_disclaimer = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor("#64748B"),
        alignment=1
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("RADIVISION AI CLINICAL SYSTEM", style_inst))
    elements.append(Paragraph("Department of Diagnostic Radiology | Automated Radiograph Screening", style_sub))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0B3D66"), spaceAfter=10))
    elements.append(Paragraph("AUTOMATED RADIOGRAPHIC DIAGNOSTIC REPORT", style_title))

    # 2. Patient & Scan Metadata Table
    clinician_name = scan_details.get("clinician_name") or "Authorized Medical Officer"
    scan_date = scan_details.get("scan_date") or datetime.now().strftime("%Y-%m-%d %H:%M")
    
    meta_data = [
        [
            Paragraph("<b>Patient Name:</b>", style_body),
            Paragraph(str(scan_details.get("patient_name", "N/A")), style_body),
            Paragraph("<b>Scan ID:</b>", style_body),
            Paragraph(f"#{scan_id}", style_body)
        ],
        [
            Paragraph("<b>Age / Gender:</b>", style_body),
            Paragraph(f"{scan_details.get('patient_age', 'N/A')} yrs / {scan_details.get('patient_gender', 'N/A')}", style_body),
            Paragraph("<b>Modality:</b>", style_body),
            Paragraph(f"{scan_details.get('scan_type', 'X-Ray')}", style_body)
        ],
        [
            Paragraph("<b>Contact:</b>", style_body),
            Paragraph(str(scan_details.get("patient_contact") or "Not on file"), style_body),
            Paragraph("<b>Body Region:</b>", style_body),
            Paragraph(str(scan_details.get("body_region") or "Standard View"), style_body)
        ],
        [
            Paragraph("<b>Reviewing Clinician:</b>", style_body),
            Paragraph(str(clinician_name), style_body),
            Paragraph("<b>Scan Date:</b>", style_body),
            Paragraph(str(scan_date), style_body)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[110, 160, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # 3. Radiograph Images Section (Raw vs Annotated)
    elements.append(Paragraph("Radiographic Imaging Comparison", style_heading))
    
    raw_img_path = scan_details.get("raw_image_path", "")
    annotated_img_path = scan_details.get("annotated_image_path", "")

    img_cells = []
    # Maximum width and height for embedded images
    target_w, target_h = 240, 180

    if os.path.exists(raw_img_path):
        try:
            img_cells.append([RLImage(raw_img_path, width=target_w, height=target_h), Paragraph("<b>Figure 1: Original Radiograph</b>", style_disclaimer)])
        except Exception:
            img_cells.append([Paragraph("<i>[Raw Image Unreadable]</i>", style_body), ""])
    else:
        img_cells.append([Paragraph("<i>[Source Image File Not Found]</i>", style_body), ""])

    if annotated_img_path and os.path.exists(annotated_img_path):
        try:
            img_cells.append([RLImage(annotated_img_path, width=target_w, height=target_h), Paragraph("<b>Figure 2: AI Annotated Overlay</b>", style_disclaimer)])
        except Exception:
            img_cells.append([Paragraph("<i>[Annotated Image Unreadable]</i>", style_body), ""])
    else:
        img_cells.append([Paragraph("<i>[No Annotated Overlay Generated]</i>", style_body), ""])

    # Organize image table side by side
    image_table_data = [
        [img_cells[0][0], img_cells[1][0]],
        [img_cells[0][1], img_cells[1][1]]
    ]
    img_table = Table(image_table_data, colWidths=[270, 270])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(img_table)
    elements.append(Spacer(1, 12))

    # 4. Diagnostic Summary & Findings Table
    elements.append(Paragraph("Detailed AI Diagnostic Findings", style_heading))

    findings = scan_details.get("findings", [])
    pred_summary = scan_details.get("prediction", "Inconclusive")
    confidence_val = scan_details.get("confidence", 0.0)

    findings_data = [
        [
            Paragraph("<b>#</b>", style_body),
            Paragraph("<b>Finding / Pathology</b>", style_body),
            Paragraph("<b>Location / Tooth #</b>", style_body),
            Paragraph("<b>Confidence</b>", style_body),
            Paragraph("<b>Diagnostic Classification</b>", style_body)
        ]
    ]

    if findings:
        for i, f in enumerate(findings, 1):
            t_num = f"Tooth #{f['tooth_number']}" if f.get("tooth_number") else scan_details.get("body_region", "General")
            c_pct = f"{f.get('confidence', 0.0) * 100:.1f}%"
            lbl = f.get("label", "N/A")
            is_abnormal = any(term in lbl.lower() for term in ["fracture", "pneumonia", "caries", "lesion"])
            status_text = "<b><font color='#E24B4A'>ABNORMAL</font></b>" if is_abnormal else "<b><font color='#639922'>NORMAL</font></b>"

            findings_data.append([
                Paragraph(str(i), style_body),
                Paragraph(lbl, style_body),
                Paragraph(t_num, style_body),
                Paragraph(c_pct, style_body),
                Paragraph(status_text, style_body)
            ])
    else:
        findings_data.append([
            Paragraph("1", style_body),
            Paragraph(pred_summary, style_body),
            Paragraph(scan_details.get("body_region", "Thoracic"), style_body),
            Paragraph(f"{confidence_val * 100:.1f}%", style_body),
            Paragraph("SUMMARY STATUS", style_body)
        ])

    find_table = Table(findings_data, colWidths=[30, 190, 120, 80, 120])
    find_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0B3D66")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(find_table)
    elements.append(Spacer(1, 14))

    # 5. Clinical Disclaimer & Signature Block
    elements.append(KeepTogether([
        Paragraph(
            "<b>Clinical Decision Support Disclaimer:</b> This report was automatically produced by RadiVision AI, "
            "an assistive deep learning prototype for academic and decision-support purposes. "
            "All findings must be independently correlated and verified by a licensed radiologist or attending physician.",
            style_disclaimer
        ),
        Spacer(1, 24),
        Table([
            [
                Paragraph("<b>Prepared by:</b> Attending Radiologist", style_body),
                Paragraph("<b>Verified by:</b> Department Chief of Radiology", style_body)
            ],
            [
                Paragraph("Department of Diagnostic Radiology", style_body),
                Paragraph("RadiVision AI Clinical Decision Support", style_body)
            ]
        ], colWidths=[270, 270])
    ]))

    doc.build(elements)
    return pdf_path

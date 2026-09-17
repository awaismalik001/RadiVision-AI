"""
excel_export.py
---------------
Professional Excel (.xlsx) PACS Database Exporter for RadiVision AI.
Generates comprehensive clinical and audit spreadsheets for system administrators:
  - Sheet 1: Patient PACS Scans & Diagnostic History
  - Sheet 2: System Activity & Security Audit Logs
  - Sheet 3: Executive Analytics & Triage Summary
"""

import os
from datetime import datetime
from typing import Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.database import db

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_excel_export(output_filename: Optional[str] = None) -> str:
    """
    Exports all patient scans, activity logs, and telemetry to an executive Excel spreadsheet.
    Returns the absolute path to the generated .xlsx file.
    """
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"RadiVision_PACS_Export_{timestamp}.xlsx"

    file_path = os.path.join(REPORTS_DIR, output_filename)

    wb = openpyxl.Workbook()

    # Define color schemes
    NAVY_HEADER = PatternFill(start_color="0B1727", end_color="0B1727", fill_type="solid")
    BLUE_ACCENT = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    WHITE_BOLD_FONT = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    TITLE_FONT = Font(name="Arial", size=14, bold=True, color="0B1727")
    REGULAR_FONT = Font(name="Arial", size=10)
    BOLD_FONT = Font(name="Arial", size=10, bold=True)

    GREEN_FILL = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    RED_FILL = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    GREEN_TEXT = Font(name="Arial", size=10, bold=True, color="065F46")
    RED_TEXT = Font(name="Arial", size=10, bold=True, color="991B1B")

    THIN_BORDER = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # -------------------------------------------------------------
    # SHEET 1: Patient PACS Scans
    # -------------------------------------------------------------
    ws_scans = wb.active
    ws_scans.title = "Patient PACS Records"

    # Title Banner
    ws_scans.merge_cells("A1:J1")
    title_cell = ws_scans["A1"]
    title_cell.value = "RADIVISION AI — CLINICAL PACS PATIENT RECORDS"
    title_cell.font = TITLE_FONT
    title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws_scans.row_dimensions[1].height = 30

    headers = [
        "Scan ID", "National ID / MRN", "Patient Name", "Age", "Gender",
        "Modality", "Body Region", "Diagnostic Impression", "Confidence", "Scan Date & Timestamp"
    ]

    for col_num, header in enumerate(headers, 1):
        cell = ws_scans.cell(row=3, column=col_num, value=header)
        cell.fill = NAVY_HEADER
        cell.font = WHITE_BOLD_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_scans.row_dimensions[3].height = 24

    scans = db.get_scans(limit=1000)
    current_row = 4
    for s in scans:
        pred = s.get("prediction", "Normal")
        conf = float(s.get("confidence", 0.0))
        is_abnormal = "abnormal" in pred.lower() or "pneumonia" in pred.lower() or "fracture" in pred.lower()

        row_data = [
            s.get("scan_id"),
            s.get("patient_contact") or f"RV-{s.get('patient_id', 100):06d}",
            s.get("patient_name", "Anonymous"),
            s.get("patient_age", 0),
            s.get("patient_gender", "Other"),
            s.get("scan_type", "Chest"),
            s.get("body_region") or ("Thorax" if s.get("scan_type") == "Chest" else "Skeletal"),
            pred,
            f"{conf * 100:.1f}%",
            str(s.get("scan_date", ""))
        ]

        for col_num, val in enumerate(row_data, 1):
            cell = ws_scans.cell(row=current_row, column=col_num, value=val)
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="center", horizontal="left" if col_num in (2, 3) else "center")

            # Highlight Diagnostic Impression
            if col_num == 8:
                cell.fill = RED_FILL if is_abnormal else GREEN_FILL
                cell.font = RED_TEXT if is_abnormal else GREEN_TEXT

        current_row += 1

    # -------------------------------------------------------------
    # SHEET 2: Activity Audit Logs
    # -------------------------------------------------------------
    ws_logs = wb.create_sheet(title="System Activity Audit")
    ws_logs.merge_cells("A1:E1")
    log_title = ws_logs["A1"]
    log_title.value = "RADIVISION AI — AUDIT & SECURITY EVENT LOGS"
    log_title.font = TITLE_FONT
    ws_logs.row_dimensions[1].height = 30

    log_headers = ["Log ID", "User ID", "Username", "Security Action", "Timestamp"]
    for col_num, header in enumerate(log_headers, 1):
        cell = ws_logs.cell(row=3, column=col_num, value=header)
        cell.fill = BLUE_ACCENT
        cell.font = WHITE_BOLD_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_logs.row_dimensions[3].height = 24

    logs = db.get_activity_logs(limit=1000)
    for row_idx, l in enumerate(logs, 4):
        ws_logs.cell(row=row_idx, column=1, value=l.get("log_id")).alignment = Alignment(horizontal="center")
        ws_logs.cell(row=row_idx, column=2, value=l.get("user_id") or "SYSTEM").alignment = Alignment(horizontal="center")
        ws_logs.cell(row=row_idx, column=3, value=l.get("username", "Unknown")).alignment = Alignment(horizontal="center")
        ws_logs.cell(row=row_idx, column=4, value=f"{l.get('action')}: {l.get('details', '')}").alignment = Alignment(horizontal="left")
        ws_logs.cell(row=row_idx, column=5, value=str(l.get("timestamp", ""))).alignment = Alignment(horizontal="center")

        for c in range(1, 6):
            ws_logs.cell(row=row_idx, column=c).border = THIN_BORDER
            ws_logs.cell(row=row_idx, column=c).font = REGULAR_FONT

    # -------------------------------------------------------------
    # Auto-Fit Column Widths Across Sheets
    # -------------------------------------------------------------
    for ws in [ws_scans, ws_logs]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row == 1:
                    continue  # Skip title row
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(file_path)
    print(f"[Excel Export] Saved PACS database export to {file_path}")
    return file_path

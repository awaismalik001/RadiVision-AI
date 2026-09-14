"""
patient_history_page.py
-----------------------
Patient history management and scan records viewer for RadiVision AI.
Implements strict role-based data partitioning:
  - Standard Clinicians: View exclusively their own submitted scans.
  - Administrators: Full visibility into institutional scans with an 'Uploaded By' column.
"""

import os
from app.qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QComboBox, QSizePolicy, Qt
)

from app.theme import (
    PRIMARY_NAVY, SECONDARY_BLUE, CARD_BG, TEXT_DARK, TEXT_MUTED,
    get_status_badge_style
)
from app.auth import SessionManager
from app.database import db
from app.report_generator import generate_pdf_report

class PatientHistoryPage(QWidget):
    """Filterable, role-aware patient records table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scans_data = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header & Filter Card
        card = QFrame(self)
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(10)

        # Title Row
        title_row = QHBoxLayout()
        self.title_lbl = QLabel("Patient Examination History", card)
        self.title_lbl.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {PRIMARY_NAVY};")
        self.title_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.title_lbl.setWordWrap(True)
        title_row.addWidget(self.title_lbl)
        card_layout.addLayout(title_row)

        # Filters Row
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit(card)
        self.search_input.setPlaceholderText("Search by Patient Name or Diagnosis...")
        self.search_input.setMinimumWidth(160)
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.search_input.textChanged.connect(self.filter_records)
        filters_row.addWidget(self.search_input, 1)

        self.type_filter = QComboBox(card)
        self.type_filter.addItems(["All Modalities", "Chest", "Bone", "Dental"])
        self.type_filter.currentIndexChanged.connect(self.filter_records)
        filters_row.addWidget(self.type_filter)

        refresh_btn = QPushButton("Refresh", card)
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_records)
        filters_row.addWidget(refresh_btn)

        card_layout.addLayout(filters_row)
        layout.addWidget(card)

        # Records Table
        self.table = QTableWidget(self)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.open_selected_report)
        layout.addWidget(self.table)

        # Action Buttons Bottom Row
        btn_row = QHBoxLayout()
        self.view_report_btn = QPushButton("View & Export Clinical PDF Report", self)
        self.view_report_btn.setCursor(Qt.PointingHandCursor)
        self.view_report_btn.clicked.connect(self.open_selected_report)
        btn_row.addWidget(self.view_report_btn)

        btn_row.addStretch()
        self.record_count_lbl = QLabel("0 records found", self)
        self.record_count_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        btn_row.addWidget(self.record_count_lbl)

        layout.addLayout(btn_row)

    def load_records(self):
        """Loads scans from SQLite based on user authorization level."""
        is_admin = SessionManager.is_admin()
        user_id = None if is_admin else SessionManager.get_user_id()

        if is_admin:
            self.title_lbl.setText("Hospital-Wide Patient Records (Administrator Audit View)")
            headers = ["Scan ID", "Patient Name", "Age/Sex", "Modality", "Diagnosis", "Confidence", "Uploaded By", "Scan Date"]
        else:
            self.title_lbl.setText("My Patient Records (Personal Uploads)")
            headers = ["Scan ID", "Patient Name", "Age/Sex", "Modality", "Diagnosis", "Confidence", "Scan Date"]

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        try:
            self.scans_data = db.get_scans(user_id=user_id)
            self.render_table(self.scans_data)
        except Exception as e:
            QMessageBox.critical(self, "Query Error", f"Failed to retrieve patient records: {str(e)}")

    def render_table(self, records):
        """Renders filtered records into the QTableWidget."""
        is_admin = SessionManager.is_admin()
        self.table.setRowCount(len(records))
        self.record_count_lbl.setText(f"{len(records)} record(s) loaded")

        for row, s in enumerate(records):
            # Format fields
            self.table.setItem(row, 0, QTableWidgetItem(f"#{s['scan_id']}"))
            self.table.setItem(row, 1, QTableWidgetItem(s['patient_name']))
            self.table.setItem(row, 2, QTableWidgetItem(f"{s['patient_age']}y / {s['patient_gender'][0]}"))
            self.table.setItem(row, 3, QTableWidgetItem(s['scan_type']))
            self.table.setItem(row, 4, QTableWidgetItem(s['prediction']))
            self.table.setItem(row, 5, QTableWidgetItem(f"{s['confidence']*100:.1f}%"))

            col_idx = 6
            if is_admin:
                clinician_label = s.get('clinician_name') or s.get('clinician_username') or 'System'
                self.table.setItem(row, col_idx, QTableWidgetItem(clinician_label))
                col_idx += 1

            self.table.setItem(row, col_idx, QTableWidgetItem(str(s['scan_date'])[:16]))

    def filter_records(self):
        """Filters displayed table rows by text search and modality."""
        q = self.search_input.text().strip().lower()
        selected_mod = self.type_filter.currentText()

        filtered = []
        for s in self.scans_data:
            match_text = (q in s['patient_name'].lower()) or (q in s['prediction'].lower())
            match_mod = (selected_mod == "All Modalities") or (s['scan_type'].lower() == selected_mod.lower())

            if match_text and match_mod:
                filtered.append(s)

        self.render_table(filtered)

    def open_selected_report(self):
        """Generates or opens the clinical PDF for the selected scan."""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "Select Record", "Please select a patient scan row from the table.")
            return

        row = selected_rows[0].row()
        scan_id_str = self.table.item(row, 0).text().replace("#", "")
        scan_id = int(scan_id_str)

        scan_details = db.get_scan_details(scan_id)
        if not scan_details:
            QMessageBox.warning(self, "Not Found", f"Details for scan #{scan_id} could not be retrieved.")
            return

        try:
            pdf_path = generate_pdf_report(scan_details)
            if os.path.exists(pdf_path):
                os.startfile(pdf_path)
            else:
                QMessageBox.information(self, "Report Saved", f"Report saved at:\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "PDF Error", f"Could not compile PDF: {str(e)}")

"""
new_scan_page.py
----------------
Modern Clinical Diagnostic Workspace for RadiVision AI (X-Ray AI).
Features:
  - Native OS Drag-and-Drop Dropzone with cloud upload icon, browse button, and format guidance.
  - 2-Column Patient Demographics Grid (Patient name & Age) matching UI mockup.
  - Non-blocking background QThread for AI inference and OpenCV/PIL visual bounding-box overlays.
  - Clean "AI prediction result" card with status icon, diagnosis, confidence score,
    and action buttons: "Export PDF report" and "Save to history".
  - High-resolution annotated radiograph viewer with site findings breakdown table.
"""

import os
from app.qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QComboBox, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QSpinBox,
    QProgressBar, QSizePolicy, QThread, Signal,
    Qt, QSize, QPixmap, QFont
)

from app.theme import (
    PRIMARY_NAVY, SECONDARY_BLUE, ACCENT_BLUE, SURFACE_1, SURFACE_2,
    BORDER_COLOR, BORDER_STRONG, TEXT_DARK, TEXT_SECONDARY, TEXT_MUTED,
    SUCCESS_GREEN, DANGER_RED, BG_DANGER, BG_SUCCESS,
    get_status_badge_style
)
from app.auth import SessionManager
from app.database import db
from app.model_engine import ai_engine
from app.detection_overlay import draw_findings_overlay
from app.report_generator import generate_pdf_report

class InferenceWorker(QThread):
    """Background worker thread executing inference and image overlays without blocking the UI."""
    inference_completed = Signal(dict, str) if Signal else None
    inference_failed = Signal(str) if Signal else None

    def __init__(self, image_path: str, confirmed_modality: str):
        super().__init__()
        self.image_path = image_path
        self.confirmed_modality = confirmed_modality

    def run(self):
        try:
            res = ai_engine.run_inference(self.image_path, self.confirmed_modality)
            annotated_path = draw_findings_overlay(
                self.image_path,
                res["findings"],
                self.confirmed_modality,
                res["prediction"],
                res["confidence"]
            )
            if self.inference_completed:
                self.inference_completed.emit(res, annotated_path)
        except Exception as e:
            if self.inference_failed:
                self.inference_failed.emit(str(e))

class ScalableImageLabel(QLabel):
    """A QLabel that maintains high-fidelity aspect ratio on dynamic window resizing."""

    def __init__(self, placeholder_text: str, parent=None):
        super().__init__(placeholder_text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(220, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.raw_pixmap = None

    def set_scalable_pixmap(self, pixmap: QPixmap):
        self.raw_pixmap = pixmap
        self.update_scaled_display()

    def update_scaled_display(self):
        if self.raw_pixmap and not self.raw_pixmap.isNull():
            w = max(self.width() - 8, 120)
            h = max(self.height() - 8, 120)
            scaled = self.raw_pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            super().setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scaled_display()

class DropZoneWidget(QFrame):
    """Native Drag & Drop Dropzone with file browse fallback matching the mockup."""
    file_dropped = Signal(str) if Signal else None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("DropZone")
        self.setStyleSheet(f"""
            #DropZone {{
                background-color: {SURFACE_1};
                border: 1.5px dashed {BORDER_STRONG};
                border-radius: 10px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        # Cloud upload icon
        icon_lbl = QLabel("☁", self)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 32px; color: {TEXT_SECONDARY};")
        layout.addWidget(icon_lbl)

        # Prompt text
        self.prompt_lbl = QLabel("Drag and drop an X-ray image, or", self)
        self.prompt_lbl.setAlignment(Qt.AlignCenter)
        self.prompt_lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        layout.addWidget(self.prompt_lbl)

        # Browse files button
        self.browse_btn = QPushButton("Browse files", self)
        self.browse_btn.setProperty("class", "secondary")
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.setFixedHeight(34)
        self.browse_btn.setFixedWidth(130)
        self.browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {TEXT_DARK};
                border: 1px solid {BORDER_STRONG};
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #F8FAFC;
                border-color: #94A3B8;
            }}
        """)
        btn_container = QHBoxLayout()
        btn_container.setAlignment(Qt.AlignCenter)
        btn_container.addWidget(self.browse_btn)
        layout.addLayout(btn_container)

        # Subtitle note
        note_lbl = QLabel("Accepts .jpg, .jpeg, .png — any resolution", self)
        note_lbl.setAlignment(Qt.AlignCenter)
        note_lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; margin-top: 4px;")
        layout.addWidget(note_lbl)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                ext = os.path.splitext(url.toLocalFile())[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    event.acceptProposedAction()
                    self.setStyleSheet(f"""
                        #DropZone {{
                            background-color: #F0F7FF;
                            border: 2px dashed {PRIMARY_NAVY};
                            border-radius: 10px;
                            padding: 20px;
                        }}
                    """)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(f"""
            #DropZone {{
                background-color: {SURFACE_1};
                border: 1.5px dashed {BORDER_STRONG};
                border-radius: 10px;
                padding: 20px;
            }}
        """)

    def dropEvent(self, event):
        self.setStyleSheet(f"""
            #DropZone {{
                background-color: {SURFACE_1};
                border: 1.5px dashed {BORDER_STRONG};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    event.acceptProposedAction()
                    if self.file_dropped:
                        self.file_dropped.emit(file_path)
                    return

    def set_loaded_file(self, filename: str):
        self.prompt_lbl.setText(f"Loaded: {filename}")
        self.prompt_lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {PRIMARY_NAVY};")

class NewScanPage(QWidget):
    """Adaptive clinical diagnostic evaluation workspace matching the UI mockup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_image_path = None
        self.annotated_image_path = None
        self.current_scan_id = None
        self.latest_scan_details = None
        self.worker = None
        self._init_ui()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content_container = QWidget()
        content_container.setStyleSheet(f"background-color: {SURFACE_2};")
        main_layout = QHBoxLayout(content_container)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(20)

        # ---------------- LEFT COLUMN: Ingestion, Demographics & Prediction Card ----------------
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        # 1. Drag-and-Drop Dropzone
        self.dropzone = DropZoneWidget(content_container)
        self.dropzone.file_dropped.connect(self.load_image_file)
        self.dropzone.browse_btn.clicked.connect(self.browse_image)
        left_col.addWidget(self.dropzone)

        # 2. Patient Demographics (2-Column Grid matching mockup)
        demo_card = QFrame(content_container)
        demo_card.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE_1};
                border: 0.5px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 14px;
            }}
        """)
        demo_layout = QVBoxLayout(demo_card)
        demo_layout.setSpacing(10)
        demo_layout.setContentsMargins(14, 14, 14, 14)

        # 2-column inputs
        grid_inputs = QGridLayout()
        grid_inputs.setHorizontalSpacing(16)
        grid_inputs.setVerticalSpacing(4)

        # Column 1: Patient name
        lbl_pname = QLabel("Patient name", demo_card)
        lbl_pname.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
        self.patient_name_input = QLineEdit(demo_card)
        self.patient_name_input.setPlaceholderText("e.g. Ali Raza")
        self.patient_name_input.setFixedHeight(36)

        grid_inputs.addWidget(lbl_pname, 0, 0)
        grid_inputs.addWidget(self.patient_name_input, 1, 0)

        # Column 2: Age
        lbl_page = QLabel("Age", demo_card)
        lbl_page.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
        self.patient_age_input = QSpinBox(demo_card)
        self.patient_age_input.setRange(1, 120)
        self.patient_age_input.setValue(34)
        self.patient_age_input.setFixedHeight(36)

        grid_inputs.addWidget(lbl_page, 0, 1)
        grid_inputs.addWidget(self.patient_age_input, 1, 1)

        demo_layout.addLayout(grid_inputs)

        # Modality selection row
        modality_row = QHBoxLayout()
        modality_row.setSpacing(8)
        self.modality_status_lbl = QLabel("Modality: Auto-detected on upload", demo_card)
        self.modality_status_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY}; font-weight: 500;")
        modality_row.addWidget(self.modality_status_lbl, 1)

        self.modality_override = QComboBox(demo_card)
        self.modality_override.addItems(["Chest", "Bone", "Dental"])
        self.modality_override.setFixedHeight(32)
        modality_row.addWidget(self.modality_override)
        demo_layout.addLayout(modality_row)

        left_col.addWidget(demo_card)

        # Progress bar for asynchronous AI inference
        self.progress_bar = QProgressBar(content_container)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #E2E8F0;
                border-radius: 2px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {PRIMARY_NAVY};
                border-radius: 2px;
            }}
        """)
        self.progress_bar.setVisible(False)
        left_col.addWidget(self.progress_bar)

        # Run AI Inference Button
        self.run_btn = QPushButton("Run AI Abnormality Detection", content_container)
        self.run_btn.setFixedHeight(40)
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self.execute_inference)
        left_col.addWidget(self.run_btn)

        # 3. AI Prediction Result Card matching the mockup
        self.pred_card = QFrame(content_container)
        self.pred_card.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE_1};
                border: 0.5px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 14px;
            }}
        """)
        pred_layout = QVBoxLayout(self.pred_card)
        pred_layout.setSpacing(12)
        pred_layout.setContentsMargins(14, 14, 14, 14)

        pred_title = QLabel("AI prediction result", self.pred_card)
        pred_title.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY}; margin-bottom: 2px;")
        pred_layout.addWidget(pred_title)

        # Result status row (Icon + Text | Confidence)
        res_row = QHBoxLayout()
        res_row.setSpacing(8)

        self.pred_icon = QLabel("🩺", self.pred_card)
        self.pred_icon.setStyleSheet(f"font-size: 18px; color: {TEXT_SECONDARY};")
        res_row.addWidget(self.pred_icon)

        self.pred_label = QLabel("Awaiting image analysis...", self.pred_card)
        self.pred_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {TEXT_DARK};")
        res_row.addWidget(self.pred_label, 1)

        self.conf_label = QLabel("Confidence: --", self.pred_card)
        self.conf_label.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        res_row.addWidget(self.conf_label)

        pred_layout.addLayout(res_row)

        # Action buttons row: [Export PDF report] [Save to history]
        btn_action_row = QHBoxLayout()
        btn_action_row.setSpacing(8)

        self.btn_export_pdf = QPushButton("Export PDF report", self.pred_card)
        self.btn_export_pdf.setProperty("class", "secondary")
        self.btn_export_pdf.setFixedHeight(34)
        self.btn_export_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_export_pdf.setEnabled(False)
        self.btn_export_pdf.clicked.connect(self.export_pdf)

        self.btn_save_history = QPushButton("Save to history", self.pred_card)
        self.btn_save_history.setProperty("class", "secondary")
        self.btn_save_history.setFixedHeight(34)
        self.btn_save_history.setCursor(Qt.PointingHandCursor)
        self.btn_save_history.setEnabled(False)
        self.btn_save_history.clicked.connect(self.save_to_history)

        btn_action_row.addWidget(self.btn_export_pdf)
        btn_action_row.addWidget(self.btn_save_history)
        pred_layout.addLayout(btn_action_row)

        left_col.addWidget(self.pred_card)
        left_col.addStretch()

        main_layout.addLayout(left_col, 5)

        # ---------------- RIGHT COLUMN: Visual Overlay & Site Findings Table ----------------
        right_col = QVBoxLayout()
        right_col.setSpacing(14)

        visual_card = QFrame(content_container)
        visual_card.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE_1};
                border: 0.5px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 14px;
            }}
        """)
        visual_layout = QVBoxLayout(visual_card)
        visual_layout.setSpacing(10)
        visual_layout.setContentsMargins(14, 14, 14, 14)

        v_title_row = QHBoxLayout()
        v_title = QLabel("Annotated Radiograph View", visual_card)
        v_title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {PRIMARY_NAVY};")
        v_title_row.addWidget(v_title)

        self.badge_status = QLabel("Ready", visual_card)
        self.badge_status.setStyleSheet(get_status_badge_style("normal"))
        v_title_row.addWidget(self.badge_status, 0, Qt.AlignRight)
        visual_layout.addLayout(v_title_row)

        # Scalable Annotated Image Display
        self.image_display = ScalableImageLabel(
            "Drop or browse a radiograph to begin triage.\nBounding-box visual overlay will render here.",
            visual_card
        )
        self.image_display.setStyleSheet("""
            background-color: #0F172A;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #94A3B8;
            font-size: 12px;
            padding: 8px;
        """)
        visual_layout.addWidget(self.image_display, 1)

        # Detailed Findings Table
        findings_lbl = QLabel("Site Detections & Measurements:", visual_card)
        findings_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY}; font-weight: 500;")
        visual_layout.addWidget(findings_lbl)

        self.findings_table = QTableWidget(visual_card)
        self.findings_table.setColumnCount(4)
        self.findings_table.setHorizontalHeaderLabels(["#", "Finding", "Location / Tooth", "Confidence"])
        self.findings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.findings_table.setMinimumHeight(130)
        self.findings_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        visual_layout.addWidget(self.findings_table)

        right_col.addWidget(visual_card, 1)
        main_layout.addLayout(right_col, 6)

        scroll.setWidget(content_container)
        outer_layout.addWidget(scroll)

    def browse_image(self):
        """Loads a radiograph file via file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Radiograph Image", "", "X-Ray Images (*.jpg *.jpeg *.png *.bmp)"
        )
        if file_path:
            self.load_image_file(file_path)

    def load_image_file(self, file_path: str):
        """Processes dropped or browsed image file."""
        if not os.path.exists(file_path):
            return

        self.selected_image_path = file_path
        filename = os.path.basename(file_path)
        self.dropzone.set_loaded_file(filename)

        # Display raw image in viewer
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.image_display.set_scalable_pixmap(pixmap)

        # Automated modality triage
        pred_modality, conf = ai_engine.detect_modality(file_path)
        self.modality_status_lbl.setText(f"Auto-Detected: {pred_modality} ({conf*100:.1f}%)")
        self.modality_override.setCurrentText(pred_modality)
        self.run_btn.setEnabled(True)

    def execute_inference(self):
        """Executes deep learning inference asynchronously."""
        if not self.selected_image_path:
            QMessageBox.warning(self, "No Image", "Please drag and drop or browse an X-ray image first.")
            return

        patient_name = self.patient_name_input.text().strip()
        if not patient_name:
            QMessageBox.warning(self, "Missing Name", "Please enter the patient's name before running inference.")
            return

        confirmed_modality = self.modality_override.currentText()

        self.run_btn.setEnabled(False)
        self.run_btn.setText("Analyzing Radiograph...")
        self.progress_bar.setVisible(True)

        self.worker = InferenceWorker(self.selected_image_path, confirmed_modality)
        if self.worker.inference_completed:
            self.worker.inference_completed.connect(self.on_inference_success)
        if self.worker.inference_failed:
            self.worker.inference_failed.connect(self.on_inference_failure)
        self.worker.start()

    def on_inference_success(self, res: dict, annotated_path: str):
        """Callback when AI inference finishes."""
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Run AI Abnormality Detection")
        self.progress_bar.setVisible(False)

        prediction_text = res["prediction"]
        confidence_val = res["confidence"]
        findings = res["findings"]
        body_region = res.get("body_region")
        confirmed_modality = self.modality_override.currentText()

        self.annotated_image_path = annotated_path
        ann_pixmap = QPixmap(annotated_path)
        if not ann_pixmap.isNull():
            self.image_display.set_scalable_pixmap(ann_pixmap)

        is_abnormal = any(term in prediction_text.lower() for term in ["abnormal", "pneumonia", "fracture", "caries", "lesion"])

        # Update Prediction Result Box matching mockup
        if is_abnormal:
            self.pred_icon.setText("⚠")
            self.pred_icon.setStyleSheet(f"font-size: 18px; color: {DANGER_RED};")
            self.pred_label.setText(f"{prediction_text} detected")
            self.pred_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {DANGER_RED};")
            self.badge_status.setText("ABNORMAL")
            self.badge_status.setStyleSheet(get_status_badge_style("abnormal"))
        else:
            self.pred_icon.setText("✓")
            self.pred_icon.setStyleSheet(f"font-size: 18px; color: {SUCCESS_GREEN};")
            self.pred_label.setText(prediction_text)
            self.pred_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {SUCCESS_GREEN};")
            self.badge_status.setText("NORMAL")
            self.badge_status.setStyleSheet(get_status_badge_style("normal"))

        self.conf_label.setText(f"Confidence: {int(confidence_val * 100)}%")

        # Populate Findings Table
        self.findings_table.setRowCount(len(findings))
        for row, f in enumerate(findings):
            self.findings_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.findings_table.setItem(row, 1, QTableWidgetItem(f["label"]))
            loc_str = f"Tooth #{f['tooth_number']}" if f.get("tooth_number") else (body_region or "Thoracic")
            self.findings_table.setItem(row, 2, QTableWidgetItem(loc_str))
            self.findings_table.setItem(row, 3, QTableWidgetItem(f"{f['confidence']*100:.1f}%"))

        # Save record into SQLite database
        try:
            patient_id = db.create_patient(
                self.patient_name_input.text().strip(),
                self.patient_age_input.value(),
                "Male",  # default
                ""
            )

            user_id = SessionManager.get_user_id() or 1
            scan_id = db.create_scan(
                patient_id=patient_id,
                user_id=user_id,
                scan_type=confirmed_modality,
                body_region=body_region,
                prediction=prediction_text,
                confidence=confidence_val,
                raw_image_path=self.selected_image_path,
                annotated_image_path=annotated_path
            )

            for f in findings:
                db.create_finding(
                    scan_id=scan_id,
                    label=f["label"],
                    tooth_number=f.get("tooth_number"),
                    confidence=f["confidence"],
                    bbox_x=f.get("bbox_x"),
                    bbox_y=f.get("bbox_y"),
                    bbox_w=f.get("bbox_w"),
                    bbox_h=f.get("bbox_h")
                )

            self.current_scan_id = scan_id
            self.latest_scan_details = db.get_scan_details(scan_id)

            self.btn_export_pdf.setEnabled(True)
            self.btn_save_history.setEnabled(True)

            db.log_activity(user_id, SessionManager.get_username(), "SCAN_PERFORMED", f"Scan #{scan_id} ({confirmed_modality})")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to persist scan record: {str(e)}")

    def on_inference_failure(self, error_msg: str):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Run AI Abnormality Detection")
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Inference Error", f"Diagnostic inference failed: {error_msg}")

    def export_pdf(self):
        """Compiles and opens the PDF clinical report."""
        if not self.latest_scan_details:
            return

        try:
            pdf_path = generate_pdf_report(self.latest_scan_details)
            user_id = SessionManager.get_user_id() or 1
            db.log_activity(user_id, SessionManager.get_username(), "PDF_EXPORTED", f"Scan #{self.current_scan_id}")
            QMessageBox.information(
                self,
                "Report Exported",
                f"Clinical PDF report generated successfully:\n\n{pdf_path}"
            )
            if os.path.exists(pdf_path):
                os.startfile(pdf_path)
        except Exception as e:
            QMessageBox.critical(self, "Report Error", f"Failed to compile PDF: {str(e)}")

    def save_to_history(self):
        """Confirms scan persistence to patient records."""
        if self.current_scan_id:
            QMessageBox.information(
                self,
                "Saved to History",
                f"Scan #{self.current_scan_id} has been securely archived to the clinical records database."
            )
            self.btn_save_history.setEnabled(False)
            self.btn_save_history.setText("Saved ✓")


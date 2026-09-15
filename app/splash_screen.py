"""
splash_screen.py
----------------
Animated Desktop Startup Splash Screen for RadiVision AI.
Displays the 3D neural compute workstation graphic with an animated
telemetry progress bar and status messages before transitioning to the login view.
"""

import os
import sys
from app.qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    Qt, QPixmap, QFont, QTimer, Signal
)

from app.theme import PRIMARY_NAVY, SECONDARY_BLUE, ACCENT_BLUE

class SplashScreen(QWidget):
    """Modern cyber-clinical desktop splash window with telemetry loading."""
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setFixedSize(680, 480)

        # Center on screen
        from app.qt_compat import QApplication
        screen_geom = QApplication.primaryScreen().geometry()
        x = (screen_geom.width() - 680) // 2
        y = (screen_geom.height() - 480) // 2
        self.move(x, y)

        self.progress_val = 0
        self.step_idx = 0
        self.boot_steps = [
            (20, "Mounting PyTorch Neural Weights & Device Cores..."),
            (45, "Loading Chest Pneumonia Classifier (90.72% Calibrated Accuracy)..."),
            (70, "Loading Bone Fracture Localization Model (91.40% Accuracy, 0.969 AUC)..."),
            (88, "Initializing GPS Healthcare & Specialist Referral Engine..."),
            (100, "All Neural Systems Online. Launching RadiVision AI Suite...")
        ]

        self.init_ui()

        # Timer for animated progress
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(35) # ~2.5 seconds total

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.setStyleSheet("""
            QWidget {
                background-color: #070B14;
                border: 1px solid #1E293B;
                border-radius: 16px;
                color: #F8FAFC;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
        """)

        # Top Header Bar
        top_bar = QHBoxLayout()
        logo_lbl = QLabel("RADIVISION")
        logo_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #FFFFFF; letter-spacing: 2px;")
        ai_lbl = QLabel("AI")
        ai_lbl.setStyleSheet("font-size: 18px; font-weight: 700; color: #06B6D4; letter-spacing: 1px;")

        badge_lbl = QLabel("CLINICAL PRO v2.0")
        badge_lbl.setStyleSheet("""
            background-color: #082F49;
            color: #38BDF8;
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid #0284C7;
        """)

        top_bar.addWidget(logo_lbl)
        top_bar.addWidget(ai_lbl)
        top_bar.addSpacing(6)
        top_bar.addWidget(badge_lbl)
        top_bar.addStretch()

        layout.addLayout(top_bar)

        # Center Graphic Image
        self.img_lbl = QLabel(self)
        self.img_lbl.setAlignment(Qt.AlignCenter)
        self.img_lbl.setFixedHeight(300)
        self.img_lbl.setStyleSheet("border-radius: 12px; background-color: #0B1120; border: 1px solid #1E293B;")

        asset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "splash_workstation.jpg")
        if os.path.exists(asset_path):
            pix = QPixmap(asset_path)
            if not pix.isNull():
                scaled = pix.scaled(640, 300, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.img_lbl.setPixmap(scaled)

        layout.addWidget(self.img_lbl)

        # Status Label
        self.status_lbl = QLabel("Initializing Neural Ingestion Pipeline...", self)
        self.status_lbl.setStyleSheet("font-size: 11px; color: #94A3B8; font-weight: 500;")
        layout.addWidget(self.status_lbl)

        # Progress Bar
        self.pbar = QProgressBar(self)
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setFixedHeight(8)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet("""
            QProgressBar {
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #06B6D4, stop:0.5 #0EA5E9, stop:1 #3B82F6);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.pbar)

    def update_progress(self):
        if self.progress_val < 100:
            self.progress_val += 1
            self.pbar.setValue(self.progress_val)

            # Update status text
            for thresh, msg in self.boot_steps:
                if self.progress_val <= thresh:
                    self.status_lbl.setText(msg)
                    break
        else:
            self.timer.stop()
            # Small delay before closing
            QTimer.singleShot(250, self.close_splash)

    def close_splash(self):
        self.close()
        self.finished.emit()

    def mousePressEvent(self, event):
        """Allow clicking anywhere to skip splash."""
        self.timer.stop()
        self.close_splash()

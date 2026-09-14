"""
main_window.py
--------------
Modern Clinical Application Shell for RadiVision AI (X-Ray AI).
Features:
  - Modern clinical sidebar with stethoscope brand, role badge (Admin in accent blue / User in teal),
    clean nav list with active highlight, and bottom logout button.
  - Contextual Top Bar with page title, subtitle, and circular user avatar ('A' / 'U').
  - Admin Dashboard Overview with 4 clean stat cards (Total scans, Abnormal detected in red,
    Registered users, Reports exported) and a live "Recent activity" feed.
  - Role-based view switching between Admin and Clinician (User).
"""

from app.qt_compat import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QMessageBox, QGridLayout,
    QScrollArea, QSizePolicy, Qt, Signal, QFont, QSize, QApplication
)

from app.theme import (
    PRIMARY_NAVY, SECONDARY_BLUE, ACCENT_BLUE, SURFACE_1, SURFACE_2,
    BORDER_COLOR, BORDER_STRONG, TEXT_DARK, TEXT_SECONDARY, TEXT_MUTED,
    SUCCESS_GREEN, DANGER_RED, BG_DANGER, BG_SUCCESS, BG_ACCENT, TEXT_ACCENT,
    BG_TEAL, TEXT_TEAL, get_role_badge_style, get_status_badge_style,
    GLOBAL_STYLESHEET,
    FONT_XS, FONT_SM, FONT_BASE, FONT_MD, FONT_LG, FONT_XL
)
from app.auth import SessionManager
from app.database import db

from app.new_scan_page import NewScanPage
from app.patient_history_page import PatientHistoryPage
from app.manage_users_page import ManageUsersPage
from app.activity_log_page import ActivityLogPage

# Pre-computed sidebar CSS strings — built once at import, reused on every toggle
# (avoids allocating a new f-string for 6+ buttons on every resize/collapse event)
_NAV_BTN_COLLAPSED_CSS = f"""
    QPushButton {{
        background-color: transparent;
        color: {TEXT_DARK};
        text-align: center;
        padding: 7px 0px;
        font-size: {FONT_MD};
        border: none;
        border-radius: 6px;
        margin: 2px 4px;
    }}
    QPushButton:checked {{
        background-color: #E0F2FE;
        color: {PRIMARY_NAVY};
        font-weight: 600;
    }}
    QPushButton:hover:!checked {{
        background-color: #F1F5F9;
    }}
"""

_NAV_BTN_EXPANDED_CSS = f"""
    QPushButton {{
        background-color: transparent;
        color: {TEXT_DARK};
        text-align: left;
        padding: 7px 10px;
        font-size: {FONT_BASE};
        font-weight: 500;
        border: none;
        border-radius: 6px;
        margin: 1px 6px;
    }}
    QPushButton:checked {{
        background-color: #E0F2FE;
        color: {PRIMARY_NAVY};
        font-weight: 600;
    }}
    QPushButton:hover:!checked {{
        background-color: #F1F5F9;
    }}
"""

_LOGOUT_COLLAPSED_CSS = f"""
    QPushButton {{
        background-color: transparent;
        text-align: center;
        padding: 7px 0px;
        font-size: {FONT_MD};
        border: none;
        border-radius: 6px;
        margin: 2px 4px;
    }}
    QPushButton:hover {{
        background-color: #FEE2E2;
    }}
"""

_LOGOUT_EXPANDED_CSS = f"""
    QPushButton {{
        background-color: transparent;
        color: {TEXT_SECONDARY};
        text-align: left;
        padding: 7px 10px;
        font-size: {FONT_BASE};
        font-weight: 500;
        border: none;
        border-radius: 6px;
        margin: 1px 6px;
    }}
    QPushButton:hover {{
        background-color: #FEE2E2;
        color: {DANGER_RED};
    }}
"""



class DashboardOverviewPage(QWidget):
    """System overview and operational metrics dashboard with adaptive scrolling."""
    navigate_to_scan = Signal() if Signal else None
    navigate_to_history = Signal() if Signal else None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_activity_data = None  # Cache to avoid full feed rebuild on identical data
        self._init_ui()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        container.setStyleSheet(f"background-color: {SURFACE_2};")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(14)

        # 1. 4 Stat Cards in a Grid matching the mockup
        self.metrics_grid = QGridLayout()
        self.metrics_grid.setSpacing(10)

        self.card_total = self._create_stat_card("Total scans", "0", TEXT_DARK)
        self.card_abnormal = self._create_stat_card("Abnormal detected", "0", DANGER_RED)
        self.card_users = self._create_stat_card("Registered users", "0", TEXT_DARK)
        self.card_reports = self._create_stat_card("Reports exported", "0", TEXT_DARK)

        self.cards = [self.card_total, self.card_abnormal, self.card_users, self.card_reports]
        self._current_cols = None
        self._reflow_metrics_grid(4)

        layout.addLayout(self.metrics_grid)

        # 2. Recent Activity Section matching the mockup
        activity_title_row = QHBoxLayout()
        activity_title = QLabel("Recent activity (all users)", container)
        activity_title.setStyleSheet(f"font-size: {FONT_SM}; font-weight: 600; color: {TEXT_SECONDARY};")
        activity_title_row.addWidget(activity_title)
        activity_title_row.addStretch()
        layout.addLayout(activity_title_row)

        self.activity_container = QFrame(container)
        self.activity_container.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE_1};
                border: 0.5px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)
        self.activity_layout.setSpacing(0)
        layout.addWidget(self.activity_container)

        # Quick Actions Bar
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)

        btn_new_scan = QPushButton("Start New Scan", container)
        btn_new_scan.setCursor(Qt.PointingHandCursor)
        btn_new_scan.setFixedHeight(32)
        if self.navigate_to_scan:
            btn_new_scan.clicked.connect(self.navigate_to_scan.emit)

        btn_history = QPushButton("View All Patient Records", container)
        btn_history.setProperty("class", "secondary")
        btn_history.setCursor(Qt.PointingHandCursor)
        btn_history.setFixedHeight(32)
        if self.navigate_to_history:
            btn_history.clicked.connect(self.navigate_to_history.emit)

        actions_row.addWidget(btn_new_scan)
        actions_row.addWidget(btn_history)
        actions_row.addStretch()
        layout.addLayout(actions_row)

        layout.addStretch()

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        if w >= 620:
            self._reflow_metrics_grid(4)
        elif w >= 380:
            self._reflow_metrics_grid(2)
        else:
            self._reflow_metrics_grid(1)

    def _reflow_metrics_grid(self, cols: int):
        if getattr(self, "_current_cols", None) == cols:
            return
        self._current_cols = cols
        for card in self.cards:
            self.metrics_grid.removeWidget(card)
        for i, card in enumerate(self.cards):
            row = i // cols
            col = i % cols
            self.metrics_grid.addWidget(card, row, col)

    def _create_stat_card(self, title: str, initial_val: str, val_color: str) -> QFrame:
        card = QFrame(self)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {SURFACE_1};
                border: 0.5px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        l = QVBoxLayout(card)
        l.setContentsMargins(10, 8, 10, 8)
        l.setSpacing(2)

        title_lbl = QLabel(title, card)
        title_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: {FONT_SM}; font-weight: 500;")

        val_lbl = QLabel(initial_val, card)
        val_lbl.setObjectName("stat_val")
        val_lbl.setStyleSheet(f"font-size: {FONT_XL}; font-weight: 600; color: {val_color}; margin-top: 2px;")

        l.addWidget(title_lbl)
        l.addWidget(val_lbl)
        return card

    def update_metrics(self):
        """Refreshes dashboard statistics and recent activity from SQLite."""
        is_admin = SessionManager.is_admin()
        user_id = None if is_admin else SessionManager.get_user_id()
        stats = db.get_dashboard_stats(user_id=user_id)

        self.card_total.findChild(QLabel, "stat_val").setText(str(stats["total_scans"]))
        self.card_abnormal.findChild(QLabel, "stat_val").setText(str(stats["abnormal_scans"]))
        self.card_users.findChild(QLabel, "stat_val").setText(str(stats["total_users"]))
        self.card_reports.findChild(QLabel, "stat_val").setText(str(stats["reports_exported"]))

        # Update Recent Activity feed
        self._populate_recent_activity(user_id)

    def _populate_recent_activity(self, user_id):
        recent = db.get_recent_scans_summary(user_id=user_id, limit=5)
        if not recent:
            # Demonstration fallbacks matching mockup
            recent = [
                {"patient_name": "Ayesha Khan", "scan_type": "Chest", "prediction": "Pneumonia", "confidence": 0.91},
                {"patient_name": "Bilal Ahmed", "scan_type": "Chest", "prediction": "Normal", "confidence": 0.97},
                {"patient_name": "Sara Iqbal", "scan_type": "Chest", "prediction": "Normal", "confidence": 0.88},
            ]

        # Skip full rebuild if data hasn't changed (performance optimization)
        cache_key = str([(r['patient_name'], r['prediction'], r['confidence']) for r in recent])
        if cache_key == self._last_activity_data:
            return
        self._last_activity_data = cache_key

        # Clear existing items
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for i, r in enumerate(recent):
            row_frame = QFrame(self.activity_container)
            is_last = (i == len(recent) - 1)
            border_bottom = "" if is_last else f"border-bottom: 0.5px solid {BORDER_COLOR};"
            row_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: transparent;
                    padding: 8px 12px;
                    {border_bottom}
                }}
            """)
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(12, 8, 12, 8)

            # Left: Patient Name — Modality X-ray
            modality_text = r['scan_type'].lower()
            left_lbl = QLabel(f"{r['patient_name']} — {modality_text} X-ray", row_frame)
            left_lbl.setStyleSheet(f"font-size: {FONT_BASE}; color: {TEXT_DARK};")
            left_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            left_lbl.setWordWrap(True)
            row_layout.addWidget(left_lbl, 1)

            # Right: Diagnosis (Confidence%)
            is_abnormal = any(term in r['prediction'].lower() for term in ["abnormal", "pneumonia", "fracture", "caries", "lesion"])
            tag_color = DANGER_RED if is_abnormal else SUCCESS_GREEN
            tag_text = f"{r['prediction']} ({int(r['confidence']*100)}%)"
            right_lbl = QLabel(tag_text, row_frame)
            right_lbl.setStyleSheet(f"font-size: {FONT_BASE}; font-weight: 500; color: {tag_color};")
            right_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row_layout.addWidget(right_lbl)

            self.activity_layout.addWidget(row_frame)

class MainWindow(QMainWindow):
    """Primary clinical application shell for RadiVision AI (X-Ray AI)."""
    logout_requested = Signal() if Signal else None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Ray AI — Clinical Abnormality Screening")
        self.setMinimumSize(700, 480)

        # Ensure window proportions fit comfortably within available desktop screen
        screen = QApplication.primaryScreen() if QApplication.instance() else None
        if screen:
            avail = screen.availableGeometry()
            init_w = min(1060, max(760, int(avail.width() * 0.82)))
            init_h = min(680, max(500, int(avail.height() * 0.82)))
            self.resize(init_w, init_h)
        else:
            self.resize(1000, 640)

        self.setStyleSheet(GLOBAL_STYLESHEET)
        self.sidebar_collapsed = False
        self.manual_toggle_override = False
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- 1. LEFT SIDEBAR matching mockup ----------------
        self.sidebar = QFrame(central_widget)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(190)
        self.sidebar.setStyleSheet(f"""
            #Sidebar {{
                background-color: {SURFACE_1};
                border-right: 0.5px solid {BORDER_COLOR};
            }}
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 12, 0, 12)
        sidebar_layout.setSpacing(2)

        # Brand header: Stethoscope icon + "X-Ray AI"
        self.brand_row = QHBoxLayout()
        self.brand_row.setContentsMargins(14, 0, 14, 8)
        self.brand_row.setSpacing(6)

        self.steth_icon = QLabel("🩺", self.sidebar)
        self.steth_icon.setStyleSheet(f"font-size: 16px; color: {TEXT_ACCENT};")
        self.brand_row.addWidget(self.steth_icon)

        self.brand_label = QLabel("X-Ray AI", self.sidebar)
        self.brand_label.setStyleSheet(f"font-size: {FONT_BASE}; font-weight: 600; color: {TEXT_DARK};")
        self.brand_row.addWidget(self.brand_label)
        self.brand_row.addStretch()
        sidebar_layout.addLayout(self.brand_row)

        # Role Badge pill
        self.role_row = QHBoxLayout()
        self.role_row.setContentsMargins(14, 0, 14, 10)
        self.role_badge = QLabel("Admin", self.sidebar)
        self.role_badge.setStyleSheet(get_role_badge_style("Admin"))
        self.role_row.addWidget(self.role_badge)
        self.role_row.addStretch()
        sidebar_layout.addLayout(self.role_row)

        # Navigation definitions: (Text, Tooltip, Stack Index, Icon)
        self.nav_items_admin = [
            ("Dashboard", "System Overview & Operational Metrics", 0, "📊"),
            ("New scan", "Upload & Evaluate Radiograph", 1, "🩻"),
            ("All patient records", "Search Hospital Patient Examinations", 2, "📋"),
            ("Reports", "Clinical Diagnostic PDF Reports", 2, "📄"),
            ("Manage users", "Manage Clinician & Admin Accounts", 3, "👥"),
            ("Activity logs", "System Audit Trail", 4, "📜"),
        ]

        self.nav_buttons = []
        for text, tooltip, target_idx, icon in self.nav_items_admin:
            btn = QPushButton(f"  {icon}  {text}", self.sidebar)
            btn.setCheckable(True)
            btn.setToolTip(f"{text} — {tooltip}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=target_idx, b=btn: self.on_nav_clicked(idx, b))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append([btn, target_idx, text, icon, tooltip])

        sidebar_layout.addStretch()

        # Logout item at bottom of sidebar
        logout_container = QVBoxLayout()
        logout_container.setContentsMargins(0, 0, 0, 0)
        self.btn_logout = QPushButton("  🚪  Logout", self.sidebar)
        self.btn_logout.setToolTip("End session and log out")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setStyleSheet(_LOGOUT_EXPANDED_CSS)
        self.btn_logout.clicked.connect(self.handle_logout)
        logout_container.addWidget(self.btn_logout)
        sidebar_layout.addLayout(logout_container)

        main_layout.addWidget(self.sidebar)

        # ---------------- 2. RIGHT MAIN CONTENT AREA ----------------
        content_area = QWidget(central_widget)
        content_area.setStyleSheet(f"background-color: {SURFACE_2};")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar matching the mockup
        top_bar = QFrame(content_area)
        top_bar.setObjectName("TopBar")
        top_bar.setStyleSheet(f"""
            #TopBar {{
                background-color: {SURFACE_2};
                border-bottom: 0.5px solid {BORDER_COLOR};
                padding: 8px 16px;
            }}
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(14, 8, 16, 8)
        top_layout.setSpacing(10)

        # Responsive Sidebar Toggle button ☰
        self.btn_toggle_sidebar = QPushButton("☰", top_bar)
        self.btn_toggle_sidebar.setFixedSize(30, 30)
        self.btn_toggle_sidebar.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_sidebar.setToolTip("Toggle sidebar navigation")
        self.btn_toggle_sidebar.setStyleSheet(f"""
            QPushButton {{
                background-color: {SURFACE_1};
                border: 0.5px solid {BORDER_COLOR};
                border-radius: 5px;
                font-size: {FONT_MD};
                font-weight: bold;
                color: {TEXT_DARK};
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: #F1F5F9;
                border-color: {BORDER_STRONG};
            }}
        """)
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        top_layout.addWidget(self.btn_toggle_sidebar)

        # Greeting & Subtitle column
        titles_col = QVBoxLayout()
        titles_col.setSpacing(1)

        self.top_title = QLabel("Welcome back, Admin", top_bar)
        self.top_title.setStyleSheet(f"font-size: {FONT_LG}; font-weight: 600; color: {TEXT_DARK};")

        self.top_subtitle = QLabel("Here's what's happening across the system.", top_bar)
        self.top_subtitle.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY};")

        titles_col.addWidget(self.top_title)
        titles_col.addWidget(self.top_subtitle)
        top_layout.addLayout(titles_col)

        top_layout.addStretch()

        # Circular Avatar Circle matching mockup (30x30)
        self.avatar_circle = QLabel("A", top_bar)
        self.avatar_circle.setFixedSize(30, 30)
        self.avatar_circle.setAlignment(Qt.AlignCenter)
        self.avatar_circle.setStyleSheet(f"""
            background-color: {BG_ACCENT};
            color: {TEXT_ACCENT};
            border-radius: 15px;
            font-size: {FONT_SM};
            font-weight: 600;
        """)
        top_layout.addWidget(self.avatar_circle)

        content_layout.addWidget(top_bar)

        # Central Stack of views
        self.stack = QStackedWidget(content_area)
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.page_dashboard = DashboardOverviewPage(self)
        if self.page_dashboard.navigate_to_scan:
            self.page_dashboard.navigate_to_scan.connect(lambda: self.switch_view(1))
        if self.page_dashboard.navigate_to_history:
            self.page_dashboard.navigate_to_history.connect(lambda: self.switch_view(2))

        self.page_scan = NewScanPage(self)
        self.page_history = PatientHistoryPage(self)
        self.page_users = ManageUsersPage(self)
        self.page_logs = ActivityLogPage(self)

        self.stack.addWidget(self.page_dashboard)  # 0
        self.stack.addWidget(self.page_scan)       # 1
        self.stack.addWidget(self.page_history)    # 2
        self.stack.addWidget(self.page_users)      # 3
        self.stack.addWidget(self.page_logs)       # 4

        content_layout.addWidget(self.stack, 1)
        main_layout.addWidget(content_area, 1)

    def toggle_sidebar(self):
        self.manual_toggle_override = True
        self.set_sidebar_collapsed(not self.sidebar_collapsed)

    def set_sidebar_collapsed(self, collapsed: bool):
        self.sidebar_collapsed = collapsed
        w = 56 if collapsed else 190
        self.sidebar.setFixedWidth(w)
        self.brand_label.setVisible(not collapsed)
        self.role_badge.setVisible(not collapsed)
        if collapsed:
            self.steth_icon.setAlignment(Qt.AlignCenter)
            self.brand_row.setContentsMargins(0, 0, 0, 8)
        else:
            self.steth_icon.setAlignment(Qt.AlignLeft)
            self.brand_row.setContentsMargins(14, 0, 14, 8)

        for item in self.nav_buttons:
            btn, t_idx, title, icon, tooltip = item
            if collapsed:
                btn.setText(icon)
                btn.setToolTip(f"{title} — {tooltip}")
                btn.setStyleSheet(_NAV_BTN_COLLAPSED_CSS)
            else:
                btn.setText(f"  {icon}  {title}")
                btn.setToolTip(f"{title} — {tooltip}")
                btn.setStyleSheet(_NAV_BTN_EXPANDED_CSS)

        if collapsed:
            self.btn_logout.setText("🚪")
            self.btn_logout.setToolTip("Logout")
            self.btn_logout.setStyleSheet(_LOGOUT_COLLAPSED_CSS)
        else:
            self.btn_logout.setText("  🚪  Logout")
            self.btn_logout.setToolTip("End session and log out")
            self.btn_logout.setStyleSheet(_LOGOUT_EXPANDED_CSS)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        if not self.manual_toggle_override:
            if w < 820 and not self.sidebar_collapsed:
                self.set_sidebar_collapsed(True)
            elif w >= 820 and self.sidebar_collapsed:
                self.set_sidebar_collapsed(False)

    def on_nav_clicked(self, target_idx: int, clicked_btn: QPushButton):
        self.switch_view(target_idx, clicked_btn)

    def switch_view(self, index: int, active_btn=None):
        """Switches central view and updates topbar header + nav button states."""
        self.stack.setCurrentIndex(index)

        # Update button check states
        for item in self.nav_buttons:
            btn, t_idx = item[0], item[1]
            if active_btn is not None:
                btn.setChecked(btn == active_btn)
            else:
                btn.setChecked(t_idx == index)

        user = SessionManager.get_user()
        user_name = user['full_name'] if user else "Admin"
        is_admin = SessionManager.is_admin()

        # Update contextual top bar titles matching mockups
        if index == 0:
            self.top_title.setText(f"Welcome back, {user_name}")
            self.top_subtitle.setText("Here's what's happening across the system.")
            self.page_dashboard.update_metrics()
        elif index == 1:
            self.top_title.setText("New X-ray scan")
            self.top_subtitle.setText("Upload an image to run AI abnormality detection.")
        elif index == 2:
            self.top_title.setText("Patient records" if not is_admin else "All patient records")
            self.top_subtitle.setText("Review examination history and clinical PDF reports.")
            self.page_history.load_records()
        elif index == 3 and is_admin:
            self.top_title.setText("Manage users")
            self.top_subtitle.setText("Authorized clinician and administrator account management.")
            self.page_users.load_users()
        elif index == 4 and is_admin:
            self.top_title.setText("Activity logs")
            self.top_subtitle.setText("Hospital security audit trail and system access history.")
            self.page_logs.load_logs()

    def update_session_view(self):
        """Configures role badge, navigation visibility, and avatar based on active session."""
        user = SessionManager.get_user()
        if not user:
            return

        is_admin = SessionManager.is_admin()
        role_str = "Admin" if is_admin else "User"

        # Update role badge pill
        self.role_badge.setText(role_str)
        self.role_badge.setStyleSheet(get_role_badge_style(role_str))

        # Update avatar circle matching mockup ('A' for Admin, 'U' for User)
        initial = "A" if is_admin else "U"
        self.avatar_circle.setText(initial)
        if is_admin:
            self.avatar_circle.setStyleSheet(f"""
                background-color: {BG_ACCENT};
                color: {TEXT_ACCENT};
                border-radius: 18px;
                font-size: {FONT_BASE};
                font-weight: 600;
            """)
        else:
            self.avatar_circle.setStyleSheet(f"""
                background-color: {BG_TEAL};
                color: {TEXT_TEAL};
                border-radius: 18px;
                font-size: {FONT_BASE};
                font-weight: 600;
            """)

        # Control visibility of nav buttons:
        # Index 0: Dashboard (visible for both)
        # Index 1: New scan (visible for both)
        # Index 2: Patient records ("All patient records" for admin, "My patient records" for user)
        # Index 3: Reports (visible for both)
        # Index 4: Manage users (Admin only)
        # Index 5: Activity logs (Admin only)
        title = "All patient records" if is_admin else "My patient records"
        self.nav_buttons[2][2] = title
        btn = self.nav_buttons[2][0]
        icon = self.nav_buttons[2][3]
        tooltip = self.nav_buttons[2][4]
        if self.sidebar_collapsed:
            btn.setText(icon)
            btn.setToolTip(f"{title} — {tooltip}")
        else:
            btn.setText(f"  {icon}  {title}")
            btn.setToolTip(f"{title} — {tooltip}")

        self.nav_buttons[4][0].setVisible(is_admin) # Manage users
        self.nav_buttons[5][0].setVisible(is_admin) # Activity logs

        # Default to Dashboard if Admin, or New Scan if User
        default_idx = 0 if is_admin else 1
        self.switch_view(default_idx)

    def handle_logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout", "Are you sure you want to end your current session?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            db.log_activity(SessionManager.get_user_id(), SessionManager.get_username(), "LOGOUT", "Session ended cleanly.")
            SessionManager.logout()
            if self.logout_requested:
                self.logout_requested.emit()

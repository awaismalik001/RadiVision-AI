"""
activity_log_page.py
--------------------
Administrator audit log viewer for RadiVision AI.
Provides an immutable chronological audit trail of all logins, uploads,
inference executions, and administrative interventions.
"""

from app.qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, Qt
)

from app.theme import PRIMARY_NAVY, CARD_BG, TEXT_MUTED
from app.database import db

class ActivityLogPage(QWidget):
    """Chronological audit trail table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logs_cache = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Card
        card = QFrame(self)
        card.setProperty("class", "card")
        card_layout = QHBoxLayout(card)

        title = QLabel("System Security & Clinical Audit Trail", card)
        title.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {PRIMARY_NAVY};")
        card_layout.addWidget(title)

        card_layout.addStretch()

        self.search_in = QLineEdit(card)
        self.search_in.setPlaceholderText("Filter audit events...")
        self.search_in.setFixedWidth(260)
        self.search_in.textChanged.connect(self.filter_logs)
        card_layout.addWidget(self.search_in)

        refresh_btn = QPushButton("Refresh Logs", card)
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_logs)
        card_layout.addWidget(refresh_btn)

        layout.addWidget(card)

        # Logs Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Log ID", "Timestamp", "User / Agent", "Action Code", "Event Details"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.count_lbl = QLabel("0 events logged", self)
        self.count_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(self.count_lbl, 0, Qt.AlignRight)

    def load_logs(self):
        """Fetches and displays activity logs from SQLite."""
        try:
            self.logs_cache = db.get_activity_logs(limit=250)
            self.render_logs(self.logs_cache)
        except Exception as e:
            QMessageBox.critical(self, "Log Error", f"Failed to retrieve logs: {str(e)}")

    def render_logs(self, logs):
        self.table.setRowCount(len(logs))
        self.count_lbl.setText(f"{len(logs)} event(s) displayed")

        for row, l in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(f"#{l['log_id']}"))
            self.table.setItem(row, 1, QTableWidgetItem(str(l['timestamp'])[:19]))
            user_str = l.get('username') or (f"User #{l['user_id']}" if l.get('user_id') else "SYSTEM")
            self.table.setItem(row, 2, QTableWidgetItem(user_str))
            self.table.setItem(row, 3, QTableWidgetItem(l['action']))
            self.table.setItem(row, 4, QTableWidgetItem(str(l.get('details') or '')))

    def filter_logs(self):
        q = self.search_in.text().strip().lower()
        if not q:
            self.render_logs(self.logs_cache)
            return

        filtered = [
            l for l in self.logs_cache
            if q in str(l['action']).lower() or q in str(l.get('username', '')).lower() or q in str(l.get('details', '')).lower()
        ]
        self.render_logs(filtered)

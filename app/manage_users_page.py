"""
manage_users_page.py
--------------------
Administrator-only user account management panel for RadiVision AI.
Allows viewing registered clinicians, modifying roles, and toggling active status.
"""

from app.qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QDialog, QLineEdit, QComboBox, Qt
)

from app.theme import PRIMARY_NAVY, SECONDARY_BLUE, DANGER_RED, SUCCESS_GREEN, CARD_BG
from app.auth import SessionManager, hash_password
from app.database import db

class AddUserDialog(QDialog):
    """Dialog for creating a new user from the admin panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add System User")
        self.setFixedSize(380, 420)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<b>Full Name:</b>"))
        self.name_in = QLineEdit(self)
        layout.addWidget(self.name_in)

        layout.addWidget(QLabel("<b>Username:</b>"))
        self.user_in = QLineEdit(self)
        layout.addWidget(self.user_in)

        layout.addWidget(QLabel("<b>Email:</b>"))
        self.email_in = QLineEdit(self)
        layout.addWidget(self.email_in)

        layout.addWidget(QLabel("<b>Temporary Password:</b>"))
        self.pass_in = QLineEdit(self)
        self.pass_in.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_in)

        layout.addWidget(QLabel("<b>Role:</b>"))
        self.role_in = QComboBox(self)
        self.role_in.addItems(["User", "Admin"])
        layout.addWidget(self.role_in)

        layout.addSpacing(10)
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Create User", self)
        save_btn.clicked.connect(self.save_user)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def save_user(self):
        name = self.name_in.text().strip()
        user = self.user_in.text().strip()
        email = self.email_in.text().strip()
        pw = self.pass_in.text()
        role = self.role_in.currentText()

        if not all([name, user, email, pw]):
            QMessageBox.warning(self, "Incomplete Form", "Please fill in all fields.")
            return

        if len(pw) < 8:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters long.")
            return

        if db.get_user_by_username(user):
            QMessageBox.warning(self, "Exists", f"Username '{user}' already exists.")
            return

        try:
            pw_hash = hash_password(pw)
            new_id = db.create_user(name, user, email, pw_hash, role)
            db.log_activity(SessionManager.get_user_id(), SessionManager.get_username(), "ADMIN_CREATED_USER", f"Created user {user} (#{new_id}) with role {role}")
            QMessageBox.information(self, "Success", f"User '{user}' created successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create user: {str(e)}")

class ManageUsersPage(QWidget):
    """Admin user accounts overview and management."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Card
        card = QFrame(self)
        card.setProperty("class", "card")
        card_layout = QHBoxLayout(card)

        title = QLabel("System User Accounts & Role Permissions", card)
        title.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {PRIMARY_NAVY};")
        card_layout.addWidget(title)

        card_layout.addStretch()

        add_btn = QPushButton("Add New User", card)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_dialog)
        card_layout.addWidget(add_btn)

        refresh_btn = QPushButton("Refresh", card)
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_users)
        card_layout.addWidget(refresh_btn)

        layout.addWidget(card)

        # Users Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["User ID", "Full Name", "Username", "Email", "Role", "Status", "Registered On"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Actions Row
        act_row = QHBoxLayout()
        self.toggle_status_btn = QPushButton("Toggle Active / Deactivate Status", self)
        self.toggle_status_btn.setProperty("class", "secondary")
        self.toggle_status_btn.clicked.connect(self.toggle_selected_user_status)
        act_row.addWidget(self.toggle_status_btn)

        self.change_role_btn = QPushButton("Toggle Role (Admin / User)", self)
        self.change_role_btn.setProperty("class", "secondary")
        self.change_role_btn.clicked.connect(self.toggle_selected_user_role)
        act_row.addWidget(self.change_role_btn)

        act_row.addStretch()
        layout.addLayout(act_row)

    def load_users(self):
        """Fetches and renders all user records."""
        try:
            users = db.get_all_users()
            self.table.setRowCount(len(users))

            for row, u in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(f"#{u['user_id']}"))
                self.table.setItem(row, 1, QTableWidgetItem(u['full_name']))
                self.table.setItem(row, 2, QTableWidgetItem(u['username']))
                self.table.setItem(row, 3, QTableWidgetItem(u['email']))
                self.table.setItem(row, 4, QTableWidgetItem(u['role']))

                status_str = "Active" if u['is_active'] else "Deactivated"
                self.table.setItem(row, 5, QTableWidgetItem(status_str))
                self.table.setItem(row, 6, QTableWidgetItem(str(u['created_at'])[:16]))

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load users: {str(e)}")

    def open_add_dialog(self):
        dlg = AddUserDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.load_users()

    def get_selected_user_id(self):
        rows = self.table.selectedItems()
        if not rows:
            QMessageBox.information(self, "Select User", "Please select a user row first.")
            return None
        row = rows[0].row()
        return int(self.table.item(row, 0).text().replace("#", ""))

    def toggle_selected_user_status(self):
        uid = self.get_selected_user_id()
        if not uid:
            return
        if uid == SessionManager.get_user_id():
            QMessageBox.warning(self, "Action Denied", "You cannot deactivate your own active session.")
            return

        user = db.get_user_by_id(uid)
        new_status = not bool(user['is_active'])
        db.update_user_status(uid, new_status)
        db.log_activity(SessionManager.get_user_id(), SessionManager.get_username(), "TOGGLE_USER_STATUS", f"User #{uid} status changed to {new_status}")
        self.load_users()

    def toggle_selected_user_role(self):
        uid = self.get_selected_user_id()
        if not uid:
            return
        if uid == SessionManager.get_user_id():
            QMessageBox.warning(self, "Action Denied", "You cannot modify your own administrative role.")
            return

        user = db.get_user_by_id(uid)
        new_role = "Admin" if user['role'] == "User" else "User"
        db.update_user_role(uid, new_role)
        db.log_activity(SessionManager.get_user_id(), SessionManager.get_username(), "CHANGE_USER_ROLE", f"User #{uid} role changed to {new_role}")
        self.load_users()

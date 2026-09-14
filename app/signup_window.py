"""
signup_window.py
----------------
Registration window for new clinicians and staff in RadiVision AI.
Enforces password complexity, email format verification, and unique constraints.
Responsive layout supporting arbitrary screen resolutions and DPI scaling.
"""

from app.qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QComboBox, QMessageBox, QScrollArea, Signal, Qt
)

from app.theme import (
    PRIMARY_NAVY, SECONDARY_BLUE, CARD_BG,
    TEXT_DARK, TEXT_MUTED, DANGER_RED, SUCCESS_GREEN, GLOBAL_STYLESHEET
)
from app.auth import hash_password, validate_password_complexity, validate_email
from app.database import db

class SignUpWindow(QWidget):
    """User account creation window with responsive layout."""
    switch_to_login = Signal() if Signal else None
    registration_successful = Signal(dict) if Signal else None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RadiVision AI — Register Account")
        self.setMinimumSize(460, 560)
        self.resize(520, 680)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 24, 30, 24)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame(container)
        card.setObjectName("SignUpCard")
        card.setMaximumWidth(480)
        card.setStyleSheet(f"""
            #SignUpCard {{
                background-color: {CARD_BG};
                border: 1px solid #CBD5E1;
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        # Title
        title = QLabel("Create New Account", card)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {PRIMARY_NAVY};")
        card_layout.addWidget(title)

        sub = QLabel("Register as an Authorized Clinician or Administrator", card)
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; margin-bottom: 6px;")
        card_layout.addWidget(sub)

        # Error / Success Label
        self.status_label = QLabel("", card)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {DANGER_RED}; font-weight: bold; font-size: 11px;")
        self.status_label.setVisible(False)
        card_layout.addWidget(self.status_label)

        # Full Name
        card_layout.addWidget(QLabel("Full Legal Name", card))
        self.name_input = QLineEdit(card)
        self.name_input.setPlaceholderText("Dr. John Doe")
        card_layout.addWidget(self.name_input)

        # Username
        card_layout.addWidget(QLabel("Username", card))
        self.user_input = QLineEdit(card)
        self.user_input.setPlaceholderText("johndoe")
        card_layout.addWidget(self.user_input)

        # Email
        card_layout.addWidget(QLabel("Institutional Email", card))
        self.email_input = QLineEdit(card)
        self.email_input.setPlaceholderText("johndoe@radivision.ai")
        card_layout.addWidget(self.email_input)

        # Password
        card_layout.addWidget(QLabel("Password (Min 8 chars, letters & numbers)", card))
        self.pass_input = QLineEdit(card)
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("••••••••")
        card_layout.addWidget(self.pass_input)

        # Confirm Password
        card_layout.addWidget(QLabel("Confirm Password", card))
        self.confirm_input = QLineEdit(card)
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("••••••••")
        card_layout.addWidget(self.confirm_input)

        # Role
        card_layout.addWidget(QLabel("Assigned Role", card))
        self.role_combo = QComboBox(card)
        self.role_combo.addItems(["User", "Admin"])
        card_layout.addWidget(self.role_combo)

        # Register Button
        card_layout.addSpacing(10)
        self.register_btn = QPushButton("Complete Registration", card)
        self.register_btn.setFixedHeight(40)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.clicked.connect(self.handle_signup)
        card_layout.addWidget(self.register_btn)

        # Toggle back to Login
        card_layout.addSpacing(6)
        login_row = QHBoxLayout()
        login_row.setAlignment(Qt.AlignCenter)
        login_lbl = QLabel("Already have an account?", card)
        login_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")

        self.back_btn = QPushButton("Sign In", card)
        self.back_btn.setStyleSheet(f"""
            background: transparent;
            color: {SECONDARY_BLUE};
            font-weight: bold;
            font-size: 12px;
            border: none;
            padding: 0;
            text-decoration: underline;
        """)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        if self.switch_to_login:
            self.back_btn.clicked.connect(self.switch_to_login.emit)

        login_row.addWidget(login_lbl)
        login_row.addWidget(self.back_btn)
        card_layout.addLayout(login_row)

        main_layout.addWidget(card)
        scroll.setWidget(container)
        root_layout.addWidget(scroll)

    def handle_signup(self):
        """Validates input fields and saves new account."""
        full_name = self.name_input.text().strip()
        username = self.user_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_input.text()
        confirm = self.confirm_input.text()
        role = self.role_combo.currentText()

        if not all([full_name, username, email, password, confirm]):
            self.show_message("Please fill out all registration fields.", is_error=True)
            return

        if not validate_email(email):
            self.show_message("Please provide a valid email address.", is_error=True)
            return

        if password != confirm:
            self.show_message("Passwords do not match.", is_error=True)
            return

        is_valid_pw, pw_msg = validate_password_complexity(password)
        if not is_valid_pw:
            self.show_message(pw_msg, is_error=True)
            return

        if db.get_user_by_username(username):
            self.show_message(f"Username '{username}' is already taken.", is_error=True)
            return

        try:
            pw_hash = hash_password(password)
            user_id = db.create_user(full_name, username, email, pw_hash, role)
            db.log_activity(user_id, username, "ACCOUNT_CREATED", f"Registered with role {role}")
            
            QMessageBox.information(self, "Registration Successful", "Your account has been successfully created. You can now sign in.")
            if self.switch_to_login:
                self.switch_to_login.emit()
        except Exception as e:
            self.show_message(f"Database error: {str(e)}", is_error=True)

    def show_message(self, text: str, is_error: bool = True):
        color = DANGER_RED if is_error else SUCCESS_GREEN
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
        self.status_label.setText(text)
        self.status_label.setVisible(True)

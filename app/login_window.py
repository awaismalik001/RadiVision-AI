"""
login_window.py
---------------
Modern Unified Clinical Authentication Window for RadiVision AI (X-Ray AI).
Provides:
  - Stethoscope circular logo in primary navy (#0B3D66)
  - Animated Segmented Tab Switcher [ Log in | Sign up ]
  - Interactive Card Shake Animation on invalid credentials
  - Animated danger error box with attempt tracking
  - Embedded Sign-up form with input validation and instant feedback
  - Seamless session transition on successful authentication
"""

from app.qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QScrollArea, QStackedWidget,
    QComboBox, QSizePolicy, Signal, Qt, QFont, QtCore
)

from app.theme import (
    PRIMARY_NAVY, SECONDARY_BLUE, SURFACE_1, SURFACE_2,
    BORDER_COLOR, BORDER_STRONG, TEXT_DARK, TEXT_SECONDARY, TEXT_MUTED,
    DANGER_RED, BG_DANGER, SUCCESS_GREEN, BG_SUCCESS, GLOBAL_STYLESHEET,
    FONT_XS, FONT_SM, FONT_BASE, FONT_MD, FONT_LG
)
from app.auth import authenticate_user, hash_password, validate_password_complexity, validate_email
from app.database import db

class SegmentedTabControl(QFrame):
    """Segmented pill slider control [ Log in | Sign up ] matching the UI mockup."""
    tab_changed = Signal(int) if Signal else None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tab = 0
        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #0B1120;
                border-radius: 8px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(4)

        self.btn_login = QPushButton("Log in", self)
        self.btn_signup = QPushButton("Sign up", self)

        for btn in [self.btn_login, self.btn_signup]:
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)

        self.btn_login.clicked.connect(lambda: self.set_active_tab(0))
        self.btn_signup.clicked.connect(lambda: self.set_active_tab(1))

        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_signup)

        self.update_styles()

    def set_active_tab(self, index: int):
        if self.current_tab != index:
            self.current_tab = index
            self.update_styles()
            if self.tab_changed:
                self.tab_changed.emit(index)

    def update_styles(self):
        active_style = f"""
            QPushButton {{
                background-color: #0891B2;
                color: #FFFFFF;
                border: 1px solid #06B6D4;
                border-radius: 6px;
                font-size: {FONT_BASE};
                font-weight: 600;
            }}
        """
        inactive_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                border-radius: 6px;
                font-size: {FONT_BASE};
                font-weight: 500;
            }}
            QPushButton:hover {{
                color: #F8FAFC;
                background-color: #1E293B;
            }}
        """
        if self.current_tab == 0:
            self.btn_login.setStyleSheet(active_style)
            self.btn_signup.setStyleSheet(inactive_style)
        else:
            self.btn_login.setStyleSheet(inactive_style)
            self.btn_signup.setStyleSheet(active_style)


class LoginWindow(QWidget):
    """Unified Clinical Authentication Window featuring Tabbed Login/Sign-up and Shake Feedback."""
    login_successful = Signal(dict) if Signal else None
    switch_to_signup = Signal() if Signal else None  # Backward compatibility

    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Ray AI — Secure Clinical Access")
        self.setMinimumSize(320, 420)
        self.resize(400, 520)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        self.attempts_remaining = 3
        self.anim_shake = None
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setAlignment(Qt.AlignCenter)

        # Centered Auth Card Frame (Responsive min/max bounds)
        self.card = QFrame(container)
        self.card.setObjectName("AuthCard")
        self.card.setMinimumWidth(280)
        self.card.setMaximumWidth(360)
        self.card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.card.setStyleSheet(f"""
            #AuthCard {{
                background-color: {SURFACE_1};
                border: 0.5px solid {BORDER_COLOR};
                border-radius: 12px;
                padding: 16px 14px;
            }}
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setSpacing(6)
        card_layout.setContentsMargins(12, 12, 12, 12)

        # 1. Circular Navy Stethoscope Logo
        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignCenter)

        logo_circle = QLabel(self.card)
        logo_circle.setFixedSize(38, 38)
        logo_circle.setAlignment(Qt.AlignCenter)
        logo_circle.setText("🩺")
        logo_circle.setStyleSheet(f"""
            background-color: {PRIMARY_NAVY};
            color: #FFFFFF;
            border-radius: 19px;
            font-size: 16px;
        """)
        logo_container.addWidget(logo_circle)
        card_layout.addLayout(logo_container)

        # Title & Subtitle
        title = QLabel("X-Ray AI system", self.card)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: {FONT_LG}; font-weight: 600; color: {TEXT_DARK}; margin-top: 2px;")
        card_layout.addWidget(title)

        subtitle = QLabel("Secure clinical access", self.card)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY}; margin-bottom: 8px;")
        card_layout.addWidget(subtitle)

        # 2. Segmented Pill Tab Switcher [ Log in | Sign up ]
        self.tab_control = SegmentedTabControl(self.card)
        self.tab_control.tab_changed.connect(self.on_tab_changed)
        card_layout.addWidget(self.tab_control)

        # 3. Stacked Forms (Index 0: Log in, Index 1: Sign up)
        self.forms_stack = QStackedWidget(self.card)

        # ---------------- FORM 1: LOG IN ----------------
        login_page = QWidget()
        login_layout = QVBoxLayout(login_page)
        login_layout.setContentsMargins(0, 6, 0, 0)
        login_layout.setSpacing(6)

        # Username Input
        lbl_user = QLabel("Username", login_page)
        lbl_user.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY}; margin-bottom: 2px;")
        login_layout.addWidget(lbl_user)

        self.login_username = QLineEdit(login_page)
        self.login_username.setPlaceholderText("e.g. dr.ahmed")
        self.login_username.setText("admin")  # Default helper
        self.login_username.setFixedHeight(30)
        login_layout.addWidget(self.login_username)

        # Password Input
        lbl_pass = QLabel("Password", login_page)
        lbl_pass.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY}; margin-bottom: 2px; margin-top: 2px;")
        login_layout.addWidget(lbl_pass)

        self.login_password = QLineEdit(login_page)
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setText("Admin123!")  # Default helper
        self.login_password.setFixedHeight(30)
        self.login_password.returnPressed.connect(self.handle_login)
        login_layout.addWidget(self.login_password)

        # Forgot Password Link
        forgot_row = QHBoxLayout()
        forgot_row.setAlignment(Qt.AlignRight)
        forgot_btn = QPushButton("Forgot password?", login_page)
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setStyleSheet(f"""
            background: transparent;
            color: {SECONDARY_BLUE};
            border: none;
            padding: 0;
            font-size: {FONT_SM};
            font-weight: 500;
        """)
        forgot_btn.clicked.connect(self.show_forgot_password_dialog)
        forgot_row.addWidget(forgot_btn)
        login_layout.addLayout(forgot_row)

        # Error Box (Banner with warning icon)
        self.err_box = QFrame(login_page)
        self.err_box.setStyleSheet(f"""
            background-color: {BG_DANGER};
            border-radius: 6px;
            padding: 6px 8px;
        """)
        err_box_layout = QHBoxLayout(self.err_box)
        err_box_layout.setContentsMargins(6, 6, 6, 6)
        err_box_layout.setSpacing(6)

        err_icon = QLabel("⚠", self.err_box)
        err_icon.setStyleSheet(f"color: {DANGER_RED}; font-size: {FONT_MD}; font-weight: bold;")
        self.err_text = QLabel("Invalid username or password.", self.err_box)
        self.err_text.setStyleSheet(f"color: {DANGER_RED}; font-size: {FONT_SM}; font-weight: 500;")
        self.err_text.setWordWrap(True)

        err_box_layout.addWidget(err_icon)
        err_box_layout.addWidget(self.err_text, 1)
        self.err_box.setVisible(False)
        login_layout.addWidget(self.err_box)

        # Log in Button
        self.btn_do_login = QPushButton("Log in", login_page)
        self.btn_do_login.setFixedHeight(32)
        self.btn_do_login.setCursor(Qt.PointingHandCursor)
        self.btn_do_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_NAVY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: {FONT_BASE};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {SECONDARY_BLUE};
            }}
        """)
        self.btn_do_login.clicked.connect(self.handle_login)
        login_layout.addWidget(self.btn_do_login)

        # Footer security note
        login_footer = QLabel("Access is logged for security and audit purposes.", login_page)
        login_footer.setAlignment(Qt.AlignCenter)
        login_footer.setStyleSheet(f"font-size: {FONT_XS}; color: {TEXT_MUTED}; margin-top: 10px;")
        login_layout.addWidget(login_footer)

        self.forms_stack.addWidget(login_page)

        # ---------------- FORM 2: SIGN UP ----------------
        signup_page = QWidget()
        signup_layout = QVBoxLayout(signup_page)
        signup_layout.setContentsMargins(0, 6, 0, 0)
        signup_layout.setSpacing(6)

        # Status notification banner for signup
        self.signup_status_box = QFrame(signup_page)
        self.signup_status_box.setStyleSheet(f"""
            background-color: {BG_DANGER};
            border-radius: 6px;
            padding: 6px 10px;
        """)
        s_box_layout = QHBoxLayout(self.signup_status_box)
        s_box_layout.setContentsMargins(6, 6, 6, 6)
        self.signup_status_lbl = QLabel("", self.signup_status_box)
        self.signup_status_lbl.setStyleSheet(f"color: {DANGER_RED}; font-size: {FONT_XS}; font-weight: 500;")
        self.signup_status_lbl.setWordWrap(True)
        s_box_layout.addWidget(self.signup_status_lbl)
        self.signup_status_box.setVisible(False)
        signup_layout.addWidget(self.signup_status_box)

        # Full name
        lbl_fname = QLabel("Full name", signup_page)
        lbl_fname.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY};")
        signup_layout.addWidget(lbl_fname)
        self.sign_name = QLineEdit(signup_page)
        self.sign_name.setPlaceholderText("e.g. Ahmed Raza")
        self.sign_name.setFixedHeight(28)
        signup_layout.addWidget(self.sign_name)

        # Username
        lbl_uname = QLabel("Username", signup_page)
        lbl_uname.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY};")
        signup_layout.addWidget(lbl_uname)
        self.sign_user = QLineEdit(signup_page)
        self.sign_user.setPlaceholderText("Choose a username")
        self.sign_user.setFixedHeight(28)
        signup_layout.addWidget(self.sign_user)

        # Email address
        lbl_email = QLabel("Email address", signup_page)
        lbl_email.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY};")
        signup_layout.addWidget(lbl_email)
        self.sign_email = QLineEdit(signup_page)
        self.sign_email.setPlaceholderText("name@hospital.com")
        self.sign_email.setFixedHeight(28)
        signup_layout.addWidget(self.sign_email)

        # Password
        lbl_spass = QLabel("Password", signup_page)
        lbl_spass.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY};")
        signup_layout.addWidget(lbl_spass)
        self.sign_pass = QLineEdit(signup_page)
        self.sign_pass.setEchoMode(QLineEdit.Password)
        self.sign_pass.setPlaceholderText("At least 8 characters")
        self.sign_pass.setFixedHeight(28)
        signup_layout.addWidget(self.sign_pass)

        # Confirm password
        lbl_sconf = QLabel("Confirm password", signup_page)
        lbl_sconf.setStyleSheet(f"font-size: {FONT_SM}; color: {TEXT_SECONDARY};")
        signup_layout.addWidget(lbl_sconf)
        self.sign_confirm = QLineEdit(signup_page)
        self.sign_confirm.setEchoMode(QLineEdit.Password)
        self.sign_confirm.setPlaceholderText("Re-enter password")
        self.sign_confirm.setFixedHeight(28)
        signup_layout.addWidget(self.sign_confirm)

        # Create account button
        signup_layout.addSpacing(4)
        self.btn_create_acc = QPushButton("Create account", signup_page)
        self.btn_create_acc.setFixedHeight(32)
        self.btn_create_acc.setCursor(Qt.PointingHandCursor)
        self.btn_create_acc.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_NAVY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: {FONT_BASE};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {SECONDARY_BLUE};
            }}
        """)
        self.btn_create_acc.clicked.connect(self.handle_signup)
        signup_layout.addWidget(self.btn_create_acc)

        # Signup footer note
        signup_footer = QLabel("New accounts are created with User access by default.", signup_page)
        signup_footer.setAlignment(Qt.AlignCenter)
        signup_footer.setStyleSheet(f"font-size: {FONT_XS}; color: {TEXT_MUTED}; margin-top: 6px;")
        signup_layout.addWidget(signup_footer)

        self.forms_stack.addWidget(signup_page)

        card_layout.addWidget(self.forms_stack)
        main_layout.addWidget(self.card)

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

    def on_tab_changed(self, index: int):
        self.forms_stack.setCurrentIndex(index)
        self.err_box.setVisible(False)
        self.signup_status_box.setVisible(False)

    def trigger_shake(self):
        """Executes a crisp left-to-right card shake animation on authentication failure."""
        if self.anim_shake is None:
            self.anim_shake = QtCore.QPropertyAnimation(self.card, b"pos")
            self.anim_shake.setDuration(400)
            self.anim_shake.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        start_pos = self.card.pos()
        self.anim_shake.stop()
        self.anim_shake.setKeyValueAt(0.0, start_pos)
        self.anim_shake.setKeyValueAt(0.2, QtCore.QPoint(start_pos.x() - 8, start_pos.y()))
        self.anim_shake.setKeyValueAt(0.4, QtCore.QPoint(start_pos.x() + 8, start_pos.y()))
        self.anim_shake.setKeyValueAt(0.6, QtCore.QPoint(start_pos.x() - 6, start_pos.y()))
        self.anim_shake.setKeyValueAt(0.8, QtCore.QPoint(start_pos.x() + 6, start_pos.y()))
        self.anim_shake.setKeyValueAt(1.0, start_pos)
        self.anim_shake.start()

    def handle_login(self):
        """Processes authentication submission."""
        username = self.login_username.text().strip()
        password = self.login_password.text()

        if not username or not password:
            self.show_login_error("Please enter both username and password.")
            self.trigger_shake()
            return

        success, msg, user_dict = authenticate_user(username, password)
        if success and user_dict:
            self.err_box.setVisible(False)
            self.attempts_remaining = 3
            if self.login_successful:
                self.login_successful.emit(user_dict)
        else:
            self.attempts_remaining = max(0, self.attempts_remaining - 1)
            err_msg = f"Invalid username or password. {self.attempts_remaining} attempts remaining."
            if self.attempts_remaining == 0:
                err_msg = "Account temporarily restricted. Please contact System Admin."
            self.show_login_error(err_msg)
            self.trigger_shake()

    def show_login_error(self, message: str):
        self.err_text.setText(message)
        self.err_box.setVisible(True)

    def handle_signup(self):
        """Validates and processes new account registration."""
        full_name = self.sign_name.text().strip()
        username = self.sign_user.text().strip()
        email = self.sign_email.text().strip()
        password = self.sign_pass.text()
        confirm = self.sign_confirm.text()
        role = "User"

        if not all([full_name, username, email, password, confirm]):
            self.show_signup_status("Please fill out all registration fields.", is_error=True)
            self.trigger_shake()
            return

        if not validate_email(email):
            self.show_signup_status("Please provide a valid email address.", is_error=True)
            self.trigger_shake()
            return

        if password != confirm:
            self.show_signup_status("Passwords do not match.", is_error=True)
            self.trigger_shake()
            return

        is_valid_pw, pw_msg = validate_password_complexity(password)
        if not is_valid_pw:
            self.show_signup_status(pw_msg, is_error=True)
            self.trigger_shake()
            return

        if db.get_user_by_username(username):
            self.show_signup_status(f"Username '{username}' is already taken.", is_error=True)
            self.trigger_shake()
            return

        try:
            pw_hash = hash_password(password)
            user_id = db.create_user(full_name, username, email, pw_hash, "User")
            db.log_activity(user_id, username, "ACCOUNT_CREATED", "Registered with role User")

            QMessageBox.information(
                self,
                "Account Created",
                f"Account for {full_name} ({username}) created successfully!\nYou may now sign in."
            )
            # Switch back to login tab and prefill username
            self.tab_control.set_active_tab(0)
            self.login_username.setText(username)
            self.login_password.clear()
            self.login_password.setFocus()
            self.show_login_error("Account created! Please enter your password to sign in.")
            self.err_box.setStyleSheet(f"background-color: {BG_SUCCESS}; border-radius: 6px; padding: 8px 10px;")
            self.err_text.setStyleSheet(f"color: {SUCCESS_GREEN}; font-size: 12px; font-weight: 500;")
        except Exception as e:
            self.show_signup_status(f"Database error: {str(e)}", is_error=True)
            self.trigger_shake()

    def show_signup_status(self, message: str, is_error: bool = True):
        bg = BG_DANGER if is_error else BG_SUCCESS
        fg = DANGER_RED if is_error else SUCCESS_GREEN
        self.signup_status_box.setStyleSheet(f"background-color: {bg}; border-radius: 6px; padding: 6px 10px;")
        self.signup_status_lbl.setStyleSheet(f"color: {fg}; font-size: 11px; font-weight: 500;")
        self.signup_status_lbl.setText(message)
        self.signup_status_box.setVisible(True)

    def show_forgot_password_dialog(self):
        QMessageBox.information(
            self,
            "Password Reset Assistance",
            "To reset clinical access credentials, please reach out to your Hospital Radiology Administrator.\n\n"
            "All credential modifications require cryptographic verification and administrative audit logging."
        )

    # Convenience aliases
    @property
    def username_input(self):
        return self.login_username

    @property
    def password_input(self):
        return self.login_password


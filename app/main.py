"""
main.py
-------
Application entry point for RadiVision AI.
Initializes the Qt event loop, establishes the SQLite database connection,
and coordinates authentication and main window transitions.
"""

import sys
import os

# Ensure the root project directory is in the Python search path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.qt_compat import check_qt_installed

if not check_qt_installed():
    sys.exit(1)

from app.qt_compat import QtWidgets, QtCore, Qt
from app.theme import GLOBAL_STYLESHEET
from app.database import db
from app.login_window import LoginWindow
from app.signup_window import SignUpWindow
from app.main_window import MainWindow

class RadiVisionApp:
    """Application controller coordinating window transitions."""

    def __init__(self):
        self.login_window = LoginWindow()
        self.signup_window = SignUpWindow()
        self.main_window = MainWindow()

        # Connect signals
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.switch_to_signup.connect(self.show_signup)

        self.signup_window.switch_to_login.connect(self.show_login)
        self.signup_window.registration_successful.connect(self.show_login)

        self.main_window.logout_requested.connect(self.on_logout)

    def start(self):
        self.login_window.show()

    def show_login(self):
        self.signup_window.hide()
        self.login_window.tab_control.set_active_tab(0)
        self.login_window.show()

    def show_signup(self):
        self.login_window.tab_control.set_active_tab(1)
        self.login_window.show()

    def on_login_success(self, user_dict):
        self.login_window.hide()
        self.signup_window.hide()
        self.main_window.update_session_view()
        self.main_window.show()

    def on_logout(self):
        self.main_window.hide()
        self.login_window.login_username.clear()
        self.login_window.login_password.clear()
        self.login_window.err_box.setVisible(False)
        self.login_window.tab_control.set_active_tab(0)
        self.login_window.show()

def main():
    # Enable high-DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("RadiVision AI")
    app.setOrganizationName("RadiVision AI")
    app.setStyleSheet(GLOBAL_STYLESHEET)

    # Initialize and start controller
    controller = RadiVisionApp()
    controller.start()

    sys.exit(app.exec_() if hasattr(app, 'exec_') else app.exec())

if __name__ == "__main__":
    main()

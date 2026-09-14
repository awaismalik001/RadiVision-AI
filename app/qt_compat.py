"""
qt_compat.py
------------
Cross-framework Qt binding compatibility layer for RadiVision AI.
Seamlessly abstracts PyQt5, PySide6, and PyQt6, exporting standard widgets
and classes so that UI code remains clean and binding-agnostic.
"""

import sys

QT_API = None

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, Qt, QSize
    from PyQt5.QtGui import QPixmap, QFont, QIcon
    QT_API = "PyQt5"
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
        from PySide6.QtCore import Signal, Slot, Qt, QSize
        from PySide6.QtGui import QPixmap, QFont, QIcon
        QT_API = "PySide6"
    except ImportError:
        try:
            from PyQt6 import QtWidgets, QtCore, QtGui
            from PyQt6.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, Qt, QSize
            from PyQt6.QtGui import QPixmap, QFont, QIcon
            QT_API = "PyQt6"
        except ImportError:
            QT_API = None

if QT_API is not None:
    # Re-export commonly used widgets
    QWidget = QtWidgets.QWidget
    QMainWindow = QtWidgets.QMainWindow
    QDialog = QtWidgets.QDialog
    QApplication = QtWidgets.QApplication
    QVBoxLayout = QtWidgets.QVBoxLayout
    QHBoxLayout = QtWidgets.QHBoxLayout
    QGridLayout = QtWidgets.QGridLayout
    QStackedWidget = QtWidgets.QStackedWidget
    QLabel = QtWidgets.QLabel
    QLineEdit = QtWidgets.QLineEdit
    QPushButton = QtWidgets.QPushButton
    QFrame = QtWidgets.QFrame
    QComboBox = QtWidgets.QComboBox
    QSpinBox = QtWidgets.QSpinBox
    QFileDialog = QtWidgets.QFileDialog
    QMessageBox = QtWidgets.QMessageBox
    QTableWidget = QtWidgets.QTableWidget
    QTableWidgetItem = QtWidgets.QTableWidgetItem
    QHeaderView = QtWidgets.QHeaderView
    QScrollArea = QtWidgets.QScrollArea
    QGroupBox = QtWidgets.QGroupBox
    QProgressBar = QtWidgets.QProgressBar
    QSizePolicy = QtWidgets.QSizePolicy
    QThread = QtCore.QThread
else:
    # Dummy fallbacks when Qt is not installed
    QWidget = object
    QMainWindow = object
    QDialog = object
    QApplication = object
    QVBoxLayout = object
    QHBoxLayout = object
    QGridLayout = object
    QStackedWidget = object
    QLabel = object
    QLineEdit = object
    QPushButton = object
    QFrame = object
    QComboBox = object
    QSpinBox = object
    QFileDialog = object
    QMessageBox = object
    QTableWidget = object
    QTableWidgetItem = object
    QHeaderView = object
    QScrollArea = object
    QGroupBox = object
    QProgressBar = object
    QSizePolicy = object
    QThread = object
    Qt = object
    Signal = None
    Slot = None
    QPixmap = object
    QFont = object
    QIcon = object
    QSize = object

def check_qt_installed() -> bool:
    """Checks if a supported Qt binding is available, providing friendly guidance if missing."""
    if QT_API is None:
        print("\n" + "=" * 65)
        print(" [RadiVision AI] Desktop UI Dependency Notice")
        print("=" * 65)
        print(" A Qt GUI binding (PyQt5 or PySide6) is required to run the desktop app.")
        print("\n Please install dependencies with pip:")
        print("     pip install -r requirements.txt")
        print("  or simply:")
        print("     pip install PyQt5")
        print("=" * 65 + "\n")
        return False
    return True

"""
theme.py
--------
Clinical Visual Design System & Styling Constants for RadiVision AI.
Adheres to the modern clinical design tokens specified in the UI/UX mockups:
  - Primary Brand Navy: #0B3D66
  - Surface-1 (Card/Container background): #FFFFFF
  - Surface-2 (Main Canvas background): #F8FAFC
  - Subtle borders: #E2E8F0, strong/dashed borders: #CBD5E1
  - Role Badges: Admin (accent blue #E0F2FE / #0B3D66), User (teal tint #E6FFFA / #0D9488)
  - Status Indicators: Danger/Abnormal (#FEE2E2 / #DC2626), Success/Normal (#DCFCE7 / #16A34A)
"""

# ----------------- Color Palette Constants -----------------
PRIMARY_NAVY    = "#0B3D66"   # Primary headers, action buttons, active tab indicator
SECONDARY_BLUE  = "#14507D"   # Links, secondary actions, section titles
ACCENT_BLUE     = "#0284C7"   # Focus states, informational highlights
SURFACE_1       = "#FFFFFF"   # Card containers, sidebar, table views, forms
SURFACE_2       = "#F8FAFC"   # Global main background canvas
BG_LIGHT        = "#F8FAFC"   # Alias for surface-2
CARD_BG         = "#FFFFFF"   # Alias for surface-1
BORDER_COLOR    = "#E2E8F0"   # Subtle card borders and separators
BORDER_HOVER    = "#CBD5E1"   # Hover borders
BORDER_STRONG   = "#CBD5E1"   # Dashed upload border, divider lines

# Role & Accent Colors
BG_ACCENT       = "#E0F2FE"   # Admin badge background
TEXT_ACCENT     = "#0B3D66"   # Admin badge text
BG_TEAL         = "#E6FFFA"   # User badge background
TEXT_TEAL       = "#0D9488"   # User badge text

# Status & Badge Colors
SUCCESS_GREEN   = "#16A34A"   # Normal / Healthy findings text
BG_SUCCESS      = "#DCFCE7"   # Normal badge background
DANGER_RED      = "#DC2626"   # Pneumonia, Fractures, Caries (Abnormal) text
BG_DANGER       = "#FEE2E2"   # Abnormal / Error alert background
WARNING_AMBER   = "#D97706"   # Inconclusive, Low-Confidence, Review Needed
BG_WARNING      = "#FEF3C7"   # Inconclusive badge background
INFO_BLUE       = "#0284C7"   # Informational badges & notices

# Typography Colors
TEXT_DARK       = "#0F172A"   # Primary titles and high-contrast typography
TEXT_SECONDARY  = "#64748B"   # Subtitles, captions, metadata
TEXT_MUTED      = "#94A3B8"   # Placeholder hints, tertiary text
TEXT_LIGHT      = "#FFFFFF"   # Text on dark navy backgrounds

# ----------------- Global Application QSS Stylesheet -----------------
GLOBAL_STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {SURFACE_2};
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    color: {TEXT_DARK};
}}

QWidget {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    color: {TEXT_DARK};
}}

/* Top Navigation Bar */
#TopBar {{
    background-color: {SURFACE_1};
    color: {TEXT_DARK};
    min-height: 56px;
    max-height: 64px;
    padding: 0 20px;
    border-bottom: 1px solid {BORDER_COLOR};
}}

#TopBar QLabel {{
    color: {TEXT_DARK};
}}

/* Left Navigation Sidebar */
#Sidebar {{
    background-color: {SURFACE_1};
    min-width: 210px;
    max-width: 210px;
    border-right: 1px solid {BORDER_COLOR};
}}

#Sidebar QPushButton {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    text-align: left;
    padding: 9px 12px;
    font-size: 13px;
    font-weight: 500;
    border: none;
    border-radius: 6px;
    margin: 1px 10px;
}}

#Sidebar QPushButton:hover {{
    background-color: #F1F5F9;
    color: {TEXT_DARK};
}}

#Sidebar QPushButton:checked, #Sidebar QPushButton[active="true"] {{
    background-color: #E2E8F0;
    color: {TEXT_DARK};
    font-weight: 600;
}}

/* Cards & Surface Panels */
QFrame.card, QWidget.card {{
    background-color: {SURFACE_1};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    padding: 16px;
}}

/* Input Fields & Combos */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {{
    background-color: #FFFFFF;
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT_DARK};
    selection-background-color: {PRIMARY_NAVY};
    selection-color: #FFFFFF;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1.5px solid {PRIMARY_NAVY};
    background-color: #FFFFFF;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border-left: 1px solid {BORDER_COLOR};
}}

/* Buttons */
QPushButton {{
    background-color: {PRIMARY_NAVY};
    color: {TEXT_LIGHT};
    border: none;
    border-radius: 6px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {SECONDARY_BLUE};
}}

QPushButton:pressed {{
    background-color: #072642;
}}

QPushButton:disabled {{
    background-color: #E2E8F0;
    color: #94A3B8;
}}

QPushButton.secondary {{
    background-color: #FFFFFF;
    color: {TEXT_DARK};
    border: 1px solid {BORDER_STRONG};
}}

QPushButton.secondary:hover {{
    background-color: #F8FAFC;
    border-color: #94A3B8;
}}

QPushButton.danger {{
    background-color: {DANGER_RED};
    color: white;
}}

QPushButton.danger:hover {{
    background-color: #B91C1C;
}}

QPushButton.success {{
    background-color: {SUCCESS_GREEN};
    color: white;
}}

QPushButton.success:hover {{
    background-color: #15803D;
}}

/* Tables */
QTableWidget, QTableView {{
    background-color: {SURFACE_1};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    gridline-color: {BORDER_COLOR};
    selection-background-color: #E0F2FE;
    selection-color: {TEXT_DARK};
    font-size: 13px;
}}

QHeaderView::section {{
    background-color: #F8FAFC;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {BORDER_COLOR};
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: #F1F5F9;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: #CBD5E1;
    min-height: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #94A3B8;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: #F1F5F9;
    height: 8px;
    margin: 0;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: #CBD5E1;
    min-width: 24px;
    border-radius: 4px;
}}
"""

def get_role_badge_style(role: str) -> str:
    """Returns CSS for role badge (Admin in accent blue, User in teal)."""
    if role.strip().lower() == "admin":
        return f"""
            background-color: {BG_ACCENT};
            color: {TEXT_ACCENT};
            border-radius: 4px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 600;
        """
    else:
        return f"""
            background-color: {BG_TEAL};
            color: {TEXT_TEAL};
            border-radius: 4px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 600;
        """

def get_status_badge_style(status_type: str) -> str:
    """Returns CSS for inline status pills (Normal, Abnormal, Inconclusive)."""
    status = status_type.lower()
    if "normal" in status or "healthy" in status:
        bg = BG_SUCCESS
        fg = SUCCESS_GREEN
        border = "#86EFAC"
    elif any(term in status for term in ["abnormal", "pneumonia", "fracture", "caries", "lesion", "danger", "error"]):
        bg = BG_DANGER
        fg = DANGER_RED
        border = "#FCA5A5"
    else:
        bg = BG_WARNING
        fg = WARNING_AMBER
        border = "#FCD34D"
        
    return f"""
        background-color: {bg};
        color: {fg};
        border: 0.5px solid {border};
        border-radius: 6px;
        padding: 3px 10px;
        font-weight: 600;
        font-size: 11px;
    """

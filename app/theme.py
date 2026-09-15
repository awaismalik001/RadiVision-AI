"""
theme.py
--------
Clinical Cyber-Visual Design System & Styling Constants for RadiVision AI.
Transforms the desktop application into the modern cyber-clinical theme:
  - Deep Cyber Canvas Background: #070B14
  - Dark Surface / Glass Panels: #0E1626 / #111827
  - Primary Brand Cyan Accent: #06B6D4 (Glow: #22D3EE)
  - Secondary Clinical Blue: #0284C7 / #2563EB
  - Crisp Light Typography: #F8FAFC / #94A3B8
  - Subtle Cyber Slate Borders: #1E293B / #334155
  - Role Badges: Admin (#082F49 / #38BDF8), User (#042F2E / #2DD4BF)
  - Status Indicators: Danger/Abnormal (#4C0519 / #EF4444), Success/Normal (#022C22 / #10B981)
"""

# ----------------- Color Palette Constants -----------------
PRIMARY_NAVY    = "#06B6D4"   # Primary Brand Cyan (accent in cyber theme)
SECONDARY_BLUE  = "#0284C7"   # Sky/Blue
ACCENT_BLUE     = "#22D3EE"   # Neon Cyan Glow
SURFACE_1       = "#0E1626"   # Dark card containers, sidebar, tables, forms
SURFACE_2       = "#070B14"   # Global main cyber canvas background
BG_LIGHT        = "#070B14"   # Alias for surface-2
CARD_BG         = "#0E1626"   # Alias for surface-1
BORDER_COLOR    = "#1E293B"   # Subtle cyber slate card borders and separators
BORDER_HOVER    = "#334155"   # Hover borders
BORDER_STRONG   = "#0284C7"   # Cyan highlight borders

# Role & Accent Colors
BG_ACCENT       = "#082F49"   # Admin badge background
TEXT_ACCENT     = "#38BDF8"   # Admin badge text
BG_TEAL         = "#042F2E"   # User badge background
TEXT_TEAL       = "#2DD4BF"   # User badge text

# Status & Badge Colors
SUCCESS_GREEN   = "#10B981"   # Normal / Healthy findings text
BG_SUCCESS      = "#022C22"   # Normal badge background
DANGER_RED      = "#EF4444"   # Pneumonia, Fractures (Abnormal) text
BG_DANGER       = "#4C0519"   # Abnormal alert background
WARNING_AMBER   = "#F59E0B"   # Inconclusive, Review Needed
BG_WARNING      = "#451A03"   # Inconclusive badge background
INFO_BLUE       = "#06B6D4"   # Informational badges & notices

# Typography Colors
TEXT_DARK       = "#F8FAFC"   # Primary high-contrast typography
TEXT_SECONDARY  = "#94A3B8"   # Subtitles, captions, metadata
TEXT_MUTED      = "#64748B"   # Placeholder hints, tertiary text
TEXT_LIGHT      = "#FFFFFF"   # Text on bright accents

# ----------------- Font Size Tokens -----------------
FONT_XS   = "9px"    # Footer notes, minimal captions, subtle badges
FONT_SM   = "10px"   # Field labels, table headers, subtitles, metadata
FONT_BASE = "11px"   # Body text, table rows, buttons, nav items
FONT_MD   = "12px"   # Card titles, section headings, radiograph label
FONT_LG   = "13px"   # Page titles, top bar heading, brand label
FONT_XL   = "16px"   # Stat card big numbers (dashboard only)

# ----------------- Global Application QSS Stylesheet -----------------
GLOBAL_STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {SURFACE_2};
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: {FONT_BASE};
    color: {TEXT_DARK};
}}

QWidget {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: {FONT_BASE};
    color: {TEXT_DARK};
}}

QLabel {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: {TEXT_DARK};
}}

/* Top Navigation Bar */
#TopBar {{
    background-color: #0D1322;
    color: {TEXT_DARK};
    min-height: 48px;
    max-height: 54px;
    padding: 0 16px;
    border-bottom: 1px solid {BORDER_COLOR};
}}

#TopBar QLabel {{
    color: {TEXT_DARK};
}}

/* Left Navigation Sidebar */
#Sidebar {{
    background-color: #0D1322;
    border-right: 1px solid {BORDER_COLOR};
}}

#Sidebar QPushButton {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    text-align: left;
    padding: 7px 10px;
    font-size: {FONT_BASE};
    font-weight: 500;
    border: 1px solid transparent;
    border-radius: 6px;
    margin: 1px 6px;
}}

#Sidebar QPushButton:hover {{
    background-color: #1E293B;
    color: #F8FAFC;
}}

#Sidebar QPushButton:checked, #Sidebar QPushButton[active="true"] {{
    background-color: rgba(6, 182, 212, 0.15);
    color: {ACCENT_BLUE};
    border: 1px solid rgba(6, 182, 212, 0.4);
    font-weight: 600;
}}

/* Cards & Surface Panels */
QFrame.card, QWidget.card, QFrame#Card, QFrame.panel {{
    background-color: {SURFACE_1};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    padding: 12px;
}}

/* Input Fields & Combos */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {{
    background-color: #0F172A;
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: {FONT_BASE};
    color: {TEXT_DARK};
    selection-background-color: #0891B2;
    selection-color: #FFFFFF;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1.5px solid {PRIMARY_NAVY};
    background-color: #0F172A;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid {BORDER_COLOR};
    background-color: #0F172A;
}}

QComboBox QAbstractItemView {{
    background-color: #0E1626;
    border: 1px solid {BORDER_COLOR};
    color: {TEXT_DARK};
    selection-background-color: #082F49;
    selection-color: #38BDF8;
}}

/* Buttons */
QPushButton {{
    background-color: #0891B2;
    color: {TEXT_LIGHT};
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 6px;
    padding: 7px 14px;
    font-size: {FONT_BASE};
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: #06B6D4;
    border: 1px solid {ACCENT_BLUE};
}}

QPushButton:pressed {{
    background-color: #0E7490;
}}

QPushButton:disabled {{
    background-color: #1E293B;
    border: 1px solid #1E293B;
    color: #64748B;
}}

QPushButton.secondary {{
    background-color: #1E293B;
    color: {TEXT_DARK};
    border: 1px solid {BORDER_HOVER};
}}

QPushButton.secondary:hover {{
    background-color: #334155;
    border-color: #475569;
    color: #FFFFFF;
}}

QPushButton.danger {{
    background-color: {DANGER_RED};
    color: white;
    border: none;
}}

QPushButton.danger:hover {{
    background-color: #DC2626;
}}

QPushButton.success {{
    background-color: {SUCCESS_GREEN};
    color: white;
    border: none;
}}

QPushButton.success:hover {{
    background-color: #059669;
}}

/* Tables */
QTableWidget, QTableView {{
    background-color: {SURFACE_1};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    gridline-color: {BORDER_COLOR};
    selection-background-color: #082F49;
    selection-color: #38BDF8;
    color: {TEXT_DARK};
    font-size: {FONT_BASE};
}}

QHeaderView::section {{
    background-color: #0B1120;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: {FONT_SM};
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {BORDER_COLOR};
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: #070B14;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: #1E293B;
    min-height: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #06B6D4;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: #070B14;
    height: 8px;
    margin: 0;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: #1E293B;
    min-width: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #06B6D4;
}}
"""

def get_role_badge_style(role: str) -> str:
    """Returns CSS for role badge (Admin in cyan, User in teal)."""
    if role.strip().lower() == "admin":
        return f"""
            background-color: {BG_ACCENT};
            color: {TEXT_ACCENT};
            border: 1px solid #0284C7;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: {FONT_SM};
            font-weight: 600;
        """
    else:
        return f"""
            background-color: {BG_TEAL};
            color: {TEXT_TEAL};
            border: 1px solid #0D9488;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: {FONT_SM};
            font-weight: 600;
        """

def get_status_badge_style(status_type: str) -> str:
    """Returns CSS for inline status pills (Normal, Abnormal, Inconclusive)."""
    status = status_type.lower()
    if "normal" in status or "healthy" in status:
        bg = BG_SUCCESS
        fg = "#34D399"
        border = "#059669"
    elif any(term in status for term in ["abnormal", "pneumonia", "fracture", "lesion", "danger", "error"]):
        bg = BG_DANGER
        fg = "#F87171"
        border = "#DC2626"
    else:
        bg = BG_WARNING
        fg = "#FBBF24"
        border = "#D97706"
        
    return f"""
        background-color: {bg};
        color: {fg};
        border: 1px solid {border};
        border-radius: 5px;
        padding: 2px 8px;
        font-weight: 600;
        font-size: {FONT_SM};
    """

"""
theme.py
--------
Zentrale Design-Tokens der Anwendung sowie die Erzeugung des globalen
Qt-Stylesheets (QSS). Alle Farb-, Radius- und Typografiewerte sind an
genau einer Stelle definiert - jede Komponente greift ausschliesslich
auf diese Konstanten zurueck, damit das Design-System konsistent bleibt.
"""

# ---------------------------------------------------------------------------
# Farbpalette (exakt wie vorgegeben)
# ---------------------------------------------------------------------------
BG_TOP = "#161311"
BG_BOTTOM = "#0a0908"
PANEL = "#121110"
PANEL_INPUT = "#181512"
BORDER = "#2c2723"

ACCENT = "#ff8a1e"
ACCENT_HOVER = "#ffa64d"
ACCENT_PRESSED = "#e26f0a"
ACCENT_RGB = (255, 138, 30)

SUCCESS = "#34d399"
ERROR = "#f87171"
WARNING = "#fbbf24"

TEXT_PRIMARY = "#f5f1ea"
TEXT_SECONDARY = "#b3aca3"
TEXT_MUTED = "#736c63"

# ---------------------------------------------------------------------------
# Radien
# ---------------------------------------------------------------------------
RADIUS_PANEL = 14
RADIUS_CONTROL = 8
RADIUS_CHIP = 8  # 6-9px Spanne -> 8px als Mittelwert fuer Chips/kleine Zeilen

# ---------------------------------------------------------------------------
# Typografie
# ---------------------------------------------------------------------------
FONT_UI = ["Segoe UI", "Inter", "SF Pro Display", "sans-serif"]
FONT_MONO = ["Cascadia Code", "JetBrains Mono", "Consolas", "monospace"]

BODY_PT = 11
LABEL_PX = 11
SECTION_TITLE_PT = 9

# ---------------------------------------------------------------------------
# Sidebar-Geometrie / Animation
# ---------------------------------------------------------------------------
SIDEBAR_COLLAPSED = 60
SIDEBAR_EXPANDED = 250
SIDEBAR_ANIM_MS = 210
SIDEBAR_COLLAPSE_DELAY_MS = 220
ICON_X = 18
LABEL_X = 50


def rgba(rgb, alpha_float):
    """rgba(...)-String mit 0-255-Alpha aus einem 0..1-Float, wie in QSS benoetigt."""
    r, g, b = rgb
    a = max(0, min(255, round(alpha_float * 255)))
    return f"rgba({r}, {g}, {b}, {a})"


def font_family_css(stack):
    return ", ".join(f'"{f}"' if " " in f and f != "sans-serif" and f != "monospace" else f for f in stack)


def build_qss() -> str:
    """Erzeugt das globale QSS fuer die gesamte Anwendung."""
    accent_soft_selected = rgba(ACCENT_RGB, 0.20)   # Sidebar / Listen-Auswahl
    accent_soft_selected2 = rgba(ACCENT_RGB, 0.25)  # Listen/Auswahl-Elemente (Spezifikation)
    hover_lighten = "rgba(255, 255, 255, 13)"       # ~5% Aufhellung
    row_hover = "rgba(255, 255, 255, 12)"

    return f"""
    /* ===================== Grundlagen ===================== */
    QWidget {{
        background-color: {PANEL};
        color: {TEXT_PRIMARY};
        font-family: {font_family_css(FONT_UI)};
        font-size: {BODY_PT}pt;
    }}

    QMainWindow, #RootBackground {{
        background-color: {BG_BOTTOM};
    }}

    QToolTip {{
        background-color: {PANEL};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 4px 8px;
        font-size: {LABEL_PX}px;
    }}

    /* ===================== Panels / Karten ===================== */
    QFrame#Panel {{
        background-color: {PANEL};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_PANEL}px;
    }}

    QLabel#PanelHeader {{
        color: {TEXT_MUTED};
        font-size: {SECTION_TITLE_PT}pt;
        font-weight: 700;
    }}

    /* ===================== Buttons ===================== */
    QPushButton {{
        background-color: {PANEL};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_CONTROL}px;
        padding: 8px 16px;
        color: {TEXT_PRIMARY};
        font-size: {BODY_PT}pt;
    }}
    QPushButton:hover {{
        border-color: {ACCENT};
        background-color: {BG_TOP};
    }}
    QPushButton:pressed {{
        border-color: {ACCENT_PRESSED};
    }}

    QPushButton#PrimaryButton {{
        background-color: {ACCENT};
        border: 1px solid {ACCENT};
        color: {BG_BOTTOM};
        font-weight: 600;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {ACCENT_HOVER};
        border-color: {ACCENT_HOVER};
    }}
    QPushButton#PrimaryButton:pressed {{
        background-color: {ACCENT_PRESSED};
        border-color: {ACCENT_PRESSED};
    }}
    QPushButton#PrimaryButton:disabled {{
        background-color: {BORDER};
        border-color: {BORDER};
        color: {TEXT_MUTED};
    }}

    /* ===================== Eingabefelder ===================== */
    QLineEdit, QPlainTextEdit, QTextEdit {{
        background-color: {PANEL_INPUT};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_CONTROL}px;
        color: {TEXT_PRIMARY};
        selection-background-color: {rgba(ACCENT_RGB, 0.35)};
        selection-color: {TEXT_PRIMARY};
        padding: 6px 10px;
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
        border: 1px solid {ACCENT};
    }}
    QLineEdit::placeholder {{
        color: {TEXT_MUTED};
    }}

    QPlainTextEdit#Editor {{
        font-family: {font_family_css(FONT_MONO)};
        border: none;
        border-radius: 0px;
        padding: 16px 18px;
    }}

    /* ===================== Vorschau (QTextBrowser) ===================== */
    QTextBrowser#Preview {{
        background-color: {PANEL};
        border: none;
        padding: 8px 10px;
    }}

    /* ===================== Statuschip ===================== */
    QLabel#StatusChip {{
        background-color: rgba(255, 255, 255, 8);
        border: 1px solid {BORDER};
        border-radius: 9px;
        color: {TEXT_SECONDARY};
        font-size: 10px;
        padding: 4px 10px;
    }}
    QLabel#StatusChip[state="busy"] {{
        color: {WARNING};
        border-color: rgba(251, 191, 36, 100);
    }}
    QLabel#StatusChip[state="ok"] {{
        color: {SUCCESS};
        border-color: rgba(52, 211, 153, 100);
    }}
    QLabel#StatusChip[state="error"] {{
        color: {ERROR};
        border-color: rgba(248, 113, 113, 100);
    }}

    /* ===================== Sidebar ===================== */
    QWidget#Sidebar {{
        background-color: {PANEL};
        border-right: 1px solid {BORDER};
    }}
    QWidget#SidebarInner {{
        background-color: transparent;
    }}

    QLabel#SectionTitle {{
        color: {TEXT_MUTED};
        font-size: {SECTION_TITLE_PT}pt;
        font-weight: 700;
    }}

    QFrame#SidebarItem {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: {RADIUS_CHIP}px;
    }}
    QFrame#SidebarItem[hovered="true"] {{
        background-color: {row_hover};
    }}
    QFrame#SidebarItem[selected="true"] {{
        background-color: {accent_soft_selected2};
        border: 1px solid {ACCENT};
    }}

    QLabel#SidebarItemLabel {{
        color: {TEXT_SECONDARY};
        font-size: {LABEL_PX}px;
    }}
    QFrame#SidebarItem[hovered="true"] QLabel#SidebarItemLabel,
    QFrame#SidebarItem[selected="true"] QLabel#SidebarItemLabel {{
        color: {TEXT_PRIMARY};
    }}

    QFrame#SidebarSeparator {{
        background-color: {BORDER};
        max-height: 1px;
        min-height: 1px;
    }}

    QToolButton#PinButton {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: {RADIUS_CHIP}px;
    }}
    QToolButton#PinButton:hover {{
        background-color: {hover_lighten};
    }}
    QToolButton#PinButton[active="true"] {{
        background-color: {accent_soft_selected};
        border: 1px solid {ACCENT};
    }}

    /* ===================== Scrollbars (schlank, transparent, Akzent bei Hover) ===================== */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {ACCENT};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        border-radius: 5px;
        min-width: 24px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {ACCENT};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}
    """

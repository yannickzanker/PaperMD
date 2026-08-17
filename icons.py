"""
icons.py
--------
Monochrome Strichzeichnungen (keine Flaechen-Icons), Strichstaerke 1.8px,
runde Linienenden/-verbindungen. Werden als SVG-Text gehalten und bei
Bedarf mit der jeweils gewuenschten Farbe in ein hochaufgeloestes QPixmap
gerendert (3-fache Aufloesung fuer scharfe Darstellung auf HiDPI-Displays).
"""

from PyQt6.QtCore import QByteArray, QSize, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

STROKE_WIDTH = 1.8

# Jedes Icon ist ein reiner <path>-Inhalt innerhalb eines 24x24 viewBox.
# {color} wird beim Rendern durch die tatsaechliche Farbe ersetzt.
_SVG_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="{color}" stroke-width="{stroke_width}"
     stroke-linecap="round" stroke-linejoin="round">
{paths}
</svg>
"""

ICON_PATHS = {
    "new_file": [
        '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9Z"/>',
        '<path d="M14 3v6h6"/>',
        '<path d="M12 12v6"/>',
        '<path d="M9 15h6"/>',
    ],
    "open_file": [
        '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>',
    ],
    "save": [
        '<path d="M5 3h11l5 5v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z"/>',
        '<path d="M9 3v6h7V3"/>',
        '<path d="M8 21v-6h8v6"/>',
    ],
    "export_pdf": [
        '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9Z"/>',
        '<path d="M14 3v6h6"/>',
        '<path d="M9.5 17.5v-4h1.1a1.3 1.3 0 0 1 0 2.6H9.5"/>',
        '<path d="M13 17.5v-4h1.6c.9 0 1.4.7 1.4 2s-.5 2-1.4 2H13Z"/>',
    ],
    "layout_split": [
        '<rect x="3" y="4" width="18" height="16" rx="2"/>',
        '<path d="M12 4v16"/>',
    ],
    "edit": [
        '<path d="M4 19 15 8l3 3-11 11H4z"/>',
        '<path d="M13 6l3 3"/>',
    ],
    "eye": [
        '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/>',
        '<circle cx="12" cy="12" r="3"/>',
    ],
    "pin": [
        '<path d="M12 17v5"/>',
        '<path d="M9 3h6l1 5-2 2v4l4 2H4l4-2v-4L6 8l1-5Z"/>',
    ],
    "trash": [
        '<path d="M3 6h18"/>',
        '<path d="M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2"/>',
        '<path d="M19 6l-1 14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1L5 6"/>',
    ],
    "info": [
        '<circle cx="12" cy="12" r="9"/>',
        '<path d="M12 16v-5"/>',
        '<path d="M12 8h.01"/>',
    ],
    "document": [
        '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9Z"/>',
        '<path d="M14 3v6h6"/>',
    ],
}


def _svg_string(name: str, color: str, stroke_width: float = STROKE_WIDTH) -> str:
    paths = "\n".join(ICON_PATHS[name])
    return _SVG_TEMPLATE.format(color=color, stroke_width=stroke_width, paths=paths)


def render_icon_pixmap(name: str, color: str, size: int = 22, device_ratio: int = 3) -> QPixmap:
    """Rendert ein Icon in der gewuenschten Farbe als scharfes HiDPI-Pixmap."""
    svg = _svg_string(name, color)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    px = QPixmap(size * device_ratio, size * device_ratio)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    px.setDevicePixelRatio(device_ratio)
    return px


def make_icon(name: str, color: str, size: int = 22) -> QIcon:
    return QIcon(render_icon_pixmap(name, color, size))

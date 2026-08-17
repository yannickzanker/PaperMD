"""
sidebar.py
----------
Schmale, permanent sichtbare Icon-Spalte am linken Rand, die beim Hovern
als Overlay auf 250px aufklappt (kein Reflow des restlichen Inhalts).

- Eingeklappte Breite: 60px / aufgeklappt: 250px
- Animationsdauer 210ms, ease-out (QEasingCurve.OutCubic)
- Verzoegerung vor automatischem Einklappen: 220ms
- Beschriftung blendet proportional zur aktuellen Breite ein (kein hartes
  Ein-/Ausblenden), Icons an fester x-Position (~18px), Beschriftung ab ~50px
- Sektionen mit Sektionstiteln und dezenten Trennlinien
- Aktiver Eintrag: rgba(255, 138, 30, 0.2) Flaeche + Akzent-Kontur
- Pin-Button haelt die Sidebar dauerhaft aufgeklappt
- Weicher Schlagschatten, proportional zum Aufklapp-Fortschritt eingeblendet
- Eigener scrollbarer Bereich, falls viele Eintraege vorhanden sind
"""

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    QTimer,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import icons
import theme


class SidebarItem(QFrame):
    """Ein klickbarer Eintrag der Sidebar mit Icon + Beschriftung."""

    clicked = pyqtSignal(str)

    def __init__(self, action_id: str, icon_name: str, label_text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarItem")
        self.action_id = action_id
        self.icon_name = icon_name
        self._selected = False
        self._hovered = False

        self.setFixedWidth(theme.SIDEBAR_EXPANDED - 16)  # feste Breite, wird vom Parent geclippt
        self.setFixedHeight(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)
        self.setProperty("hovered", False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(theme.ICON_X, 0, 12, 0)
        layout.setSpacing(0)

        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(22, 22)
        self.icon_label.setPixmap(
            icons.render_icon_pixmap(icon_name, theme.TEXT_SECONDARY, 20)
        )
        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignVCenter)

        layout.addSpacing(theme.LABEL_X - theme.ICON_X - 22)

        self.text_label = QLabel(label_text, self)
        self.text_label.setObjectName("SidebarItemLabel")
        self.text_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.text_label, 1, Qt.AlignmentFlag.AlignVCenter)

        self._opacity_effect = QGraphicsOpacityEffect(self.text_label)
        self._opacity_effect.setOpacity(0.0)
        self.text_label.setGraphicsEffect(self._opacity_effect)

        self._full_label_text = label_text

    def set_reveal_progress(self, progress: float):
        """progress: 0.0 (eingeklappt) .. 1.0 (aufgeklappt) - steuert die Label-Opazitaet."""
        self._opacity_effect.setOpacity(max(0.0, min(1.0, progress)))

    def set_selected(self, selected: bool):
        self._selected = selected
        self.setProperty("selected", selected)
        self._repolish()

    def enterEvent(self, event):
        self._hovered = True
        self.setProperty("hovered", True)
        self._repolish()
        self.icon_label.setPixmap(
            icons.render_icon_pixmap(self.icon_name, theme.TEXT_PRIMARY, 20)
        )
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.setProperty("hovered", False)
        self._repolish()
        color = theme.TEXT_PRIMARY if self._selected else theme.TEXT_SECONDARY
        self.icon_label.setPixmap(icons.render_icon_pixmap(self.icon_name, color, 20))
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.action_id)
        super().mousePressEvent(event)

    def _repolish(self):
        self.style().unpolish(self)
        self.style().polish(self)


class SectionTitle(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SectionTitle")
        self.setContentsMargins(theme.LABEL_X, 6, 12, 6)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

    def set_reveal_progress(self, progress: float):
        self._opacity_effect.setOpacity(max(0.0, min(1.0, progress)))


class Separator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarSeparator")
        self.setFrameShape(QFrame.Shape.HLine)
        self.setContentsMargins(12, 0, 12, 0)


class Sidebar(QWidget):
    """Die eigentliche Hover-Sidebar. Wird als frei positioniertes Overlay
    (kein Layout-Reflow) ueber dem Hauptinhalt platziert."""

    action_triggered = pyqtSignal(str)   # z.B. "new", "open", "save", "export_pdf"
    view_changed = pyqtSignal(str)       # "split", "editor", "preview"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setMouseTracking(True)
        self._pinned = False
        self._width = theme.SIDEBAR_COLLAPSED
        self._reveal_items = []  # SidebarItem/SectionTitle-Instanzen fuer Opacity-Update

        self._collapse_timer = QTimer(self)
        self._collapse_timer.setSingleShot(True)
        self._collapse_timer.setInterval(theme.SIDEBAR_COLLAPSE_DELAY_MS)
        self._collapse_timer.timeout.connect(self._collapse)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(18, 0)
        self._shadow.setBlurRadius(40)
        self._shadow.setColor(QColor(0, 0, 0, 0))
        self.setGraphicsEffect(self._shadow)

        self._animation = QPropertyAnimation(self, b"sidebarWidth", self)
        self._animation.setDuration(theme.SIDEBAR_ANIM_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_width_changed)

        self._build_ui()
        self.resize(theme.SIDEBAR_COLLAPSED, self.height())

    # -- animierte Breite als Qt-Property -------------------------------
    def _get_width(self):
        return self._width

    def _set_width(self, value):
        self._width = value
        self.setFixedWidth(int(value))

    sidebarWidth = pyqtProperty(int, _get_width, _set_width)

    # -- Aufbau -----------------------------------------------------------
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Fixe Innenbreite (250px) - wird durch die animierte Aussenbreite geclippt
        self.inner = QWidget(self)
        self.inner.setObjectName("SidebarInner")
        self.inner.setFixedWidth(theme.SIDEBAR_EXPANDED)
        outer.addWidget(self.inner)

        inner_layout = QVBoxLayout(self.inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        # -- Pin-Zeile --
        pin_row = QWidget(self.inner)
        pin_row.setFixedHeight(52)
        pin_layout = QHBoxLayout(pin_row)
        pin_layout.setContentsMargins(theme.ICON_X, 0, 12, 0)
        self.pin_button = QToolButton(pin_row)
        self.pin_button.setObjectName("PinButton")
        self.pin_button.setFixedSize(32, 32)
        self.pin_button.setIcon(icons.make_icon("pin", theme.TEXT_SECONDARY, 16))
        self.pin_button.setIconSize(QSize(16, 16))
        self.pin_button.setToolTip("Sidebar fixieren")
        self.pin_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_button.clicked.connect(self._toggle_pin)
        pin_layout.addWidget(self.pin_button, 0, Qt.AlignmentFlag.AlignVCenter)
        pin_layout.addStretch(1)
        pin_row.setStyleSheet(f"border-bottom: 1px solid {theme.BORDER};")
        inner_layout.addWidget(pin_row)

        # -- Scrollbarer Bereich fuer die Eintraege --
        scroll = QScrollArea(self.inner)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        inner_layout.addWidget(scroll, 1)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(0, 8, 0, 12)
        self._content_layout.setSpacing(2)
        scroll.setWidget(content)

        # -- Sektion: Datei --
        self._add_section_title("Datei")
        self._add_item("new", "new_file", "Neues Dokument")
        self._add_item("open", "open_file", "Markdown öffnen…")
        self._add_item("save_md", "save", "Als .md speichern")

        # -- Sektion: Export --
        self._add_separator()
        self._add_section_title("Export")
        self._add_item("export_pdf", "export_pdf", "Als PDF exportieren")

        # -- Sektion: Ansicht --
        self._add_separator()
        self._add_section_title("Ansicht")
        self.view_items = {
            "split": self._add_item("view_split", "layout_split", "Geteilte Ansicht"),
            "editor": self._add_item("view_editor", "edit", "Nur Editor"),
            "preview": self._add_item("view_preview", "eye", "Nur Vorschau"),
        }
        self.view_items["split"].set_selected(True)

        # -- Sektion: Info --
        self._add_separator()
        self._add_section_title("Info")
        self.word_count_item = self._add_item("noop", "info", "0 Wörter", clickable=False)

        self._content_layout.addStretch(1)

    def _add_section_title(self, text):
        title = SectionTitle(text, self.inner)
        self._content_layout.addWidget(title)
        self._reveal_items.append(title)

    def _add_separator(self):
        self._content_layout.addWidget(Separator(self.inner))

    def _add_item(self, action_id, icon_name, label, clickable=True):
        item = SidebarItem(action_id, icon_name, label, self.inner)
        if clickable:
            item.clicked.connect(self._on_item_clicked)
        else:
            item.setCursor(Qt.CursorShape.ArrowCursor)
        self._content_layout.addWidget(item)
        self._reveal_items.append(item)
        return item

    def _on_item_clicked(self, action_id: str):
        if action_id.startswith("view_"):
            view_id = action_id.replace("view_", "")
            for key, item in self.view_items.items():
                item.set_selected(key == view_id)
            self.view_changed.emit(view_id)
        else:
            self.action_triggered.emit(action_id)

    def set_word_count_text(self, text: str):
        self.word_count_item.text_label.setText(text)

    # -- Hover-Verhalten ----------------------------------------------------
    def enterEvent(self, event):
        self._collapse_timer.stop()
        self._expand()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._pinned:
            self._collapse_timer.start()
        super().leaveEvent(event)

    def _toggle_pin(self):
        self._pinned = not self._pinned
        self.pin_button.setProperty("active", self._pinned)
        self.pin_button.style().unpolish(self.pin_button)
        self.pin_button.style().polish(self.pin_button)
        if self._pinned:
            self._collapse_timer.stop()
            self._expand()
        else:
            self._collapse()

    def _expand(self):
        self._animation.stop()
        self._animation.setStartValue(self._width)
        self._animation.setEndValue(theme.SIDEBAR_EXPANDED)
        self._animation.start()

    def _collapse(self):
        if self._pinned:
            return
        self._animation.stop()
        self._animation.setStartValue(self._width)
        self._animation.setEndValue(theme.SIDEBAR_COLLAPSED)
        self._animation.start()

    def _on_width_changed(self, value):
        span = theme.SIDEBAR_EXPANDED - theme.SIDEBAR_COLLAPSED
        progress = (value - theme.SIDEBAR_COLLAPSED) / span if span else 1.0
        progress = max(0.0, min(1.0, progress))
        for item in self._reveal_items:
            item.set_reveal_progress(progress)
        # Schlagschatten proportional zum Aufklapp-Fortschritt einblenden
        self._shadow.setBlurRadius(40 * progress)
        self._shadow.setColor(QColor(0, 0, 0, int(115 * progress)))

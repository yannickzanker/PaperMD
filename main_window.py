"""
main_window.py
---------------
Fuegt alle Bausteine zur eigentlichen Anwendung zusammen:

- Sidebar als frei positioniertes Overlay ganz links (kein Reflow des
  Inhalts, der Content-Bereich reserviert dauerhaft die eingeklappte
  Breite von 60px als linken Rand)
- Kopfzeile mit Dateiname-Feld, Status-Chip, "Leeren"- und
  "Als PDF exportieren"-Button (primaer)
- Editor (QPlainTextEdit, Monospace) und Live-Vorschau (QTextBrowser)
  in zwei Panels (Karten-Radius 14px, Rahmenfarbe)
- Datei-Operationen: Neu / Oeffnen / Speichern als .md
- PDF-Export ueber QPrinter + QTextDocument (kein zusaetzlicher
  Web-Engine-Unterbau noetig -> laeuft ueberall dort, wo PyQt6 laeuft)
"""

import os

from PyQt6.QtCore import QMarginsF, QTimer, Qt
from PyQt6.QtGui import QFont, QPageLayout, QPageSize, QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

import icons
import markdown_engine
import theme
from sidebar import Sidebar

DEFAULT_MARKDOWN = """# Willkommen

Dies ist ein **Markdown-zu-PDF-Konverter**. Schreibe links deinen Text, \
rechts siehst du die Live-Vorschau.

## Funktionen

- Live-Vorschau
- Export als sauber formatierte PDF-Datei
- Öffnen und Speichern von `.md`-Dateien

> Tipp: Fahre mit der Maus über die Sidebar links, um zwischen Editor, \
geteilter Ansicht und Vorschau zu wechseln.

```
def gruss(name):
    return f"Hallo, {name}!"
```

| Funktion | Status |
|---|---|
| Markdown-Parsing | fertig |
| PDF-Export | fertig |
"""


class Panel(QFrame):
    """Karten-Panel mit Kopfzeile, entspricht dem Karten-Radius/Rahmen des Design-Systems."""

    def __init__(self, title: str, icon_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget(self)
        header.setFixedHeight(36)
        header.setStyleSheet(f"border-bottom: 1px solid {theme.BORDER};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 0, 14, 0)
        header_layout.setSpacing(8)

        icon_label = QLabel(header)
        icon_label.setPixmap(icons.render_icon_pixmap(icon_name, theme.TEXT_MUTED, 14))
        header_layout.addWidget(icon_label)

        title_label = QLabel(title, header)
        title_label.setObjectName("PanelHeader")
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)

        layout.addWidget(header)
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.body_layout, 1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown → PDF")
        self.resize(1280, 820)
        self.current_md_path = None

        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(150)
        self._render_timer.timeout.connect(self._render_preview)

        self._status_reset_timer = QTimer(self)
        self._status_reset_timer.setSingleShot(True)
        self._status_reset_timer.timeout.connect(lambda: self._set_status("Bereit", None))

        self._build_ui()
        self.editor.setPlainText(DEFAULT_MARKDOWN)
        self._render_preview()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QWidget(self)
        root.setObjectName("RootBackground")
        self.setCentralWidget(root)

        # Der Content-Bereich reserviert dauerhaft 60px am linken Rand
        # (= eingeklappte Sidebar-Breite). Die Sidebar selbst liegt als
        # Overlay ueber diesem Rand und wird beim Aufklappen NICHT Teil
        # des Layouts - es findet kein Reflow statt.
        self.content = QWidget(root)
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(24, 20, 24, 24)
        content_layout.setSpacing(16)

        # -- Kopfzeile --
        topbar = QHBoxLayout()
        topbar.setSpacing(12)

        filename_wrap = QFrame(self.content)
        filename_wrap.setStyleSheet(
            f"QFrame {{ background-color: {theme.PANEL_INPUT}; border: 1px solid {theme.BORDER}; "
            f"border-radius: {theme.RADIUS_CONTROL}px; }}"
        )
        fw_layout = QHBoxLayout(filename_wrap)
        fw_layout.setContentsMargins(10, 0, 10, 0)
        fw_layout.setSpacing(8)
        fw_icon = QLabel(filename_wrap)
        fw_icon.setPixmap(icons.render_icon_pixmap("document", theme.TEXT_MUTED, 16))
        fw_layout.addWidget(fw_icon)
        self.filename_input = QLineEdit("dokument", filename_wrap)
        self.filename_input.setStyleSheet("background: transparent; border: none;")
        fw_layout.addWidget(self.filename_input, 1)
        suffix = QLabel(".pdf", filename_wrap)
        suffix.setStyleSheet(f"color: {theme.TEXT_MUTED};")
        fw_layout.addWidget(suffix)
        filename_wrap.setFixedHeight(38)
        topbar.addWidget(filename_wrap, 1)

        self.status_chip = QLabel("Bereit", self.content)
        self.status_chip.setObjectName("StatusChip")
        topbar.addWidget(self.status_chip)

        clear_btn = QPushButton("Leeren", self.content)
        clear_btn.setIcon(icons.make_icon("trash", theme.TEXT_PRIMARY, 16))
        clear_btn.clicked.connect(self._clear_editor)
        topbar.addWidget(clear_btn)

        export_btn = QPushButton("Als PDF exportieren", self.content)
        export_btn.setObjectName("PrimaryButton")
        export_btn.setIcon(icons.make_icon("export_pdf", theme.BG_BOTTOM, 16))
        export_btn.clicked.connect(self._export_pdf)
        topbar.addWidget(export_btn)
        self.export_btn = export_btn

        content_layout.addLayout(topbar)

        # -- Panels: Editor + Vorschau --
        panes_layout = QHBoxLayout()
        panes_layout.setSpacing(16)

        self.editor_panel = Panel("Markdown", "edit", self.content)
        self.editor = QPlainTextEdit(self.editor_panel)
        self.editor.setObjectName("Editor")
        self.editor.setFont(QFont(theme.FONT_MONO[0], theme.BODY_PT))
        self.editor.setPlaceholderText("# Titel\n\nSchreibe hier dein Markdown …")
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor_panel.body_layout.addWidget(self.editor)

        self.preview_panel = Panel("Vorschau", "eye", self.content)
        self.preview = QTextBrowser(self.preview_panel)
        self.preview.setObjectName("Preview")
        self.preview.setOpenExternalLinks(True)
        self.preview_panel.body_layout.addWidget(self.preview)

        panes_layout.addWidget(self.editor_panel, 1)
        panes_layout.addWidget(self.preview_panel, 1)
        content_layout.addLayout(panes_layout, 1)

        # -- Sidebar (Overlay, ueber dem Content) --
        self.sidebar = Sidebar(root)
        self.sidebar.action_triggered.connect(self._on_sidebar_action)
        self.sidebar.view_changed.connect(self._on_view_changed)
        self.sidebar.raise_()

        self._reposition()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition()

    def _reposition(self):
        root = self.centralWidget()
        if root is None:
            return
        w, h = root.width(), root.height()
        self.content.setGeometry(theme.SIDEBAR_COLLAPSED, 0, max(0, w - theme.SIDEBAR_COLLAPSED), h)
        self.sidebar.setGeometry(0, 0, self.sidebar.sidebarWidth, h)

    # ------------------------------------------------------------------
    # Ansicht umschalten (Editor / Geteilt / Vorschau)
    def _on_view_changed(self, view_id: str):
        if view_id == "editor":
            self.editor_panel.show()
            self.preview_panel.show()
            self.preview_panel.hide()
        elif view_id == "preview":
            self.editor_panel.hide()
            self.preview_panel.show()
        else:
            self.editor_panel.show()
            self.preview_panel.show()

    # ------------------------------------------------------------------
    # Sidebar-Aktionen
    def _on_sidebar_action(self, action_id: str):
        if action_id == "new":
            self._new_document()
        elif action_id == "open":
            self._open_document()
        elif action_id == "save_md":
            self._save_markdown()
        elif action_id == "export_pdf":
            self._export_pdf()

    # ------------------------------------------------------------------
    def _on_text_changed(self):
        self._render_timer.start()
        words = len(self.editor.toPlainText().split())
        label = "1 Wort" if words == 1 else f"{words} Wörter"
        self.sidebar.set_word_count_text(label)

    def _render_preview(self):
        self.preview.setHtml(markdown_engine.preview_html(self.editor.toPlainText()))

    def _set_status(self, text: str, state):
        self.status_chip.setText(text)
        self.status_chip.setProperty("state", state)
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)

    # ------------------------------------------------------------------
    # Datei-Operationen
    def _new_document(self):
        if self.editor.toPlainText().strip():
            reply = QMessageBox.question(
                self, "Neues Dokument",
                "Aktuellen Inhalt verwerfen und neues Dokument beginnen?",
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.editor.clear()
        self.filename_input.setText("dokument")
        self.current_md_path = None

    def _open_document(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Markdown öffnen", "", "Markdown-Dateien (*.md *.markdown *.txt);;Alle Dateien (*)"
        )
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            self.editor.setPlainText(f.read())
        base = os.path.splitext(os.path.basename(path))[0]
        self.filename_input.setText(base)
        self.current_md_path = path

    def _save_markdown(self):
        default_name = (self.filename_input.text().strip() or "dokument") + ".md"
        path, _ = QFileDialog.getSaveFileName(self, "Markdown speichern", default_name, "Markdown-Dateien (*.md)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())
        self.current_md_path = path
        self._set_status("Gespeichert", "ok")
        self._status_reset_timer.start(2000)

    def _clear_editor(self):
        if not self.editor.toPlainText().strip():
            return
        reply = QMessageBox.question(self, "Leeren", "Editor-Inhalt wirklich leeren?")
        if reply == QMessageBox.StandardButton.Yes:
            self.editor.clear()

    # ------------------------------------------------------------------
    # PDF-Export ueber QPrinter + QTextDocument
    def _export_pdf(self):
        text = self.editor.toPlainText()
        if not text.strip():
            self._set_status("Nichts zu exportieren", "busy")
            self._status_reset_timer.start(1600)
            return

        default_name = (self.filename_input.text().strip() or "dokument") + ".pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Als PDF exportieren", default_name, "PDF-Dateien (*.pdf)")
        if not path:
            return

        self._set_status("Erzeuge PDF …", "busy")
        self.export_btn.setEnabled(False)
        try:
            document = QTextDocument()
            document.setHtml(markdown_engine.export_html(text))

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            printer.setPageMargins(QMarginsF(28, 28, 28, 28), QPageLayout.Unit.Millimeter)

            document.setPageSize(printer.pageRect(QPrinter.Unit.DevicePixel).size())
            document.print(printer)

            self._set_status("PDF exportiert", "ok")
        except Exception as exc:  # pragma: no cover - defensive UI-Feedback
            self._set_status("Export fehlgeschlagen", "error")
            QMessageBox.critical(self, "Fehler beim Export", str(exc))
        finally:
            self.export_btn.setEnabled(True)
            self._status_reset_timer.start(2200)

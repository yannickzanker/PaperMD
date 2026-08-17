"""
main.py
-------
Startet die PyQt6-Anwendung "Markdown → PDF".

Ausfuehren:
    python main.py

Abhaengigkeiten siehe requirements.txt.
"""

import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

import theme
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown → PDF")

    base_font = QFont(theme.FONT_UI[0])
    base_font.setPointSize(theme.BODY_PT)
    app.setFont(base_font)

    app.setStyleSheet(theme.build_qss())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

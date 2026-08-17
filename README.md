# Markdown → PDF (PyQt6)

Desktop-Tool zum Schreiben von Markdown mit Live-Vorschau und PDF-Export,
umgesetzt nach dem vorgegebenen Design-System (Farben, Radien, Typografie,
Komponenten-Zustände, Apple-artige Hover-Sidebar).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Start

```bash
python main.py
```

## Projektstruktur

| Datei | Zweck |
|---|---|
| `main.py` | Einstiegspunkt, wendet globales QSS an |
| `theme.py` | Alle Design-Tokens + QSS-Generator (einzige Quelle der Wahrheit für Farben/Radien) |
| `icons.py` | Monochrome SVG-Strichicons, gerendert als scharfe HiDPI-Pixmaps |
| `sidebar.py` | Hover-Sidebar (60px → 250px, Overlay, Pin, proportionales Reveal, Schlagschatten) |
| `markdown_engine.py` | Markdown → HTML, getrennte Templates für Vorschau (dunkel) und PDF-Export (hell) |
| `main_window.py` | Hauptfenster, Layout, Datei-Operationen, PDF-Export |

## Funktionen

- Live-Vorschau während des Schreibens (Debounce 150 ms)
- Ansichten: geteilt / nur Editor / nur Vorschau (über die Sidebar)
- Markdown öffnen (`.md`/`.markdown`/`.txt`) und speichern
- PDF-Export über `QPrinter` + `QTextDocument` — kein zusätzlicher
  Web-Engine-Unterbau nötig, läuft überall dort, wo PyQt6 selbst läuft

## Bekannte Einschränkung

Qt' rich-text-Engine (`QTextBrowser`/`QTextDocument`) unterstützt nur eine
Teilmenge von CSS — insbesondere **kein** `border-radius` und **kein**
`box-shadow` innerhalb des gerenderten Markdown-*Inhalts*. Die App-Chrome
(Sidebar, Buttons, Panels, Inputs) setzt daher alle geforderten Radien und
Zustände über natives Qt-Styling (QSS) um; nur der aus Markdown gerenderte
Text selbst (Überschriften, Code-Blöcke, Zitate) verwendet eckige Kästen
statt abgerundeter Ecken, da Qt das dort nicht rendert.

Falls stattdessen pixelgenaues CSS3 auch im gerenderten Inhalt gewünscht
ist, lässt sich `preview.py`/`markdown_engine.py` leicht auf
`QWebEngineView` (PyQt6-WebEngine) umstellen — dann rendert Chromium und
`page().printToPdf()` übernimmt den Export 1:1 wie im Browser.

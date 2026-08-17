"""
markdown_engine.py
-------------------
Wandelt Markdown-Text in HTML um (python-markdown) und bettet ihn in
eines von zwei Templates ein:

- preview_html(): dunkles Theme, exakt nach Design-System, fuer die
  Live-Vorschau in der App (QTextBrowser).
- export_html(): helles, druckfreundliches Papier-Theme fuer den
  PDF-Export - Akzentfarbe wird dort nur sparsam als Auszeichnung
  (Ueberschriften-Unterstreichung, Links, Zitat-Leiste) eingesetzt.

Beide nutzen dieselbe Markdown-Konvertierung, damit Vorschau und PDF
inhaltlich stets identisch sind.

Hinweis: QTextBrowser/QTextDocument rendern nur eine Teilmenge von CSS
(kein border-radius, kein box-shadow, kein Flexbox). Die App-Chrome
(Sidebar, Buttons, Panels) nutzt daher QSS fuer alle in der Vorgabe
geforderten Radien/Zustaende; innerhalb des gerenderten Markdown-Inhalts
selbst werden nur die von Qt unterstuetzten CSS-Eigenschaften verwendet.
"""

import markdown as md_lib

import theme

_MD_EXTENSIONS = ["extra", "sane_lists", "fenced_code", "tables", "codehilite", "toc"]
_MD_EXTENSION_CFG = {
    "codehilite": {"guess_lang": False, "noclasses": True},
}


def markdown_to_html_body(markdown_text: str) -> str:
    if not markdown_text.strip():
        return ""
    converter = md_lib.Markdown(
        extensions=_MD_EXTENSIONS,
        extension_configs=_MD_EXTENSION_CFG,
        output_format="html5",
    )
    return converter.convert(markdown_text)


def preview_html(markdown_text: str) -> str:
    body = markdown_to_html_body(markdown_text)
    if not body:
        body = f'<p style="color:{theme.TEXT_MUTED}; font-style:italic;">Die Vorschau erscheint hier, sobald du zu schreiben beginnst.</p>'

    mono = theme.FONT_MONO[0]
    return f"""
    <html>
    <head>
    <style>
      body {{
        font-family: '{theme.FONT_UI[0]}', '{theme.FONT_UI[1]}', sans-serif;
        font-size: {theme.BODY_PT}pt;
        color: {theme.TEXT_PRIMARY};
        background-color: {theme.PANEL};
        line-height: 1.6;
      }}
      h1, h2, h3, h4 {{
        color: {theme.TEXT_PRIMARY};
        font-weight: 700;
      }}
      h1 {{ font-size: 20pt; border-bottom: 1px solid {theme.BORDER}; padding-bottom: 4px; }}
      h2 {{ font-size: 16pt; border-bottom: 1px solid {theme.BORDER}; padding-bottom: 3px; }}
      h3 {{ font-size: 13pt; }}
      p {{ color: {theme.TEXT_PRIMARY}; }}
      a {{ color: {theme.ACCENT}; }}
      code {{
        font-family: '{mono}';
        background-color: {theme.PANEL_INPUT};
        color: {theme.ACCENT_HOVER};
        border: 1px solid {theme.BORDER};
        padding: 1px 5px;
      }}
      pre {{
        background-color: {theme.PANEL_INPUT};
        border: 1px solid {theme.BORDER};
        padding: 10px;
      }}
      pre code {{
        background-color: transparent;
        border: none;
        color: {theme.TEXT_PRIMARY};
      }}
      blockquote {{
        color: {theme.TEXT_SECONDARY};
        border-left: 3px solid {theme.ACCENT};
        background-color: {theme.rgba(theme.ACCENT_RGB, 0.08)};
        padding: 4px 14px;
        margin: 8px 0;
      }}
      table {{ border-collapse: collapse; }}
      th, td {{
        border: 1px solid {theme.BORDER};
        padding: 5px 10px;
      }}
      th {{
        background-color: {theme.PANEL_INPUT};
        color: {theme.TEXT_SECONDARY};
      }}
      hr {{ border: none; border-top: 1px solid {theme.BORDER}; }}
    </style>
    </head>
    <body>{body}</body>
    </html>
    """


def export_html(markdown_text: str, title: str = "") -> str:
    """Helles, druckfreundliches Papier-Theme fuer den PDF-Export."""
    body = markdown_to_html_body(markdown_text)
    heading = f"<h1>{title}</h1>" if title else ""
    return f"""
    <html>
    <head>
    <style>
      body {{
        font-family: '{theme.FONT_UI[0]}', '{theme.FONT_UI[1]}', sans-serif;
        font-size: 11pt;
        color: #1a1a1a;
        background-color: #ffffff;
        line-height: 1.55;
      }}
      h1, h2, h3, h4 {{ color: #161311; font-weight: 700; }}
      h1 {{ font-size: 22pt; border-bottom: 2px solid {theme.ACCENT}; padding-bottom: 5px; }}
      h2 {{ font-size: 16pt; border-bottom: 1px solid #e5e0d8; padding-bottom: 4px; }}
      h3 {{ font-size: 13pt; }}
      a {{ color: {theme.ACCENT_PRESSED}; }}
      code {{
        font-family: '{theme.FONT_MONO[0]}';
        background-color: #f4f1ea;
        color: #a2530c;
        border: 1px solid #e5e0d8;
        padding: 1px 5px;
      }}
      pre {{
        background-color: #f4f1ea;
        border: 1px solid #e5e0d8;
        padding: 10px;
      }}
      pre code {{ background-color: transparent; border: none; color: #3a352e; }}
      blockquote {{
        border-left: 3px solid {theme.ACCENT};
        background-color: #fff4e9;
        color: #4a453d;
        padding: 4px 14px;
        margin: 8px 0;
      }}
      table {{ border-collapse: collapse; }}
      th, td {{ border: 1px solid #e5e0d8; padding: 5px 10px; }}
      th {{ background-color: #f4f1ea; }}
      hr {{ border: none; border-top: 1px solid #e5e0d8; }}
    </style>
    </head>
    <body>{heading}{body}</body>
    </html>
    """

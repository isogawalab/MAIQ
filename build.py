#!/usr/bin/env python3
"""Render index.html from project.json.

Usage: python3 build.py [project.json] [index.html]

Only the Python standard library is used. Fields named "html" are inserted
as-is, so they may contain inline markup (<strong>, <code>, entities).
All other strings are escaped.
"""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent

ICONS = {
    "paper": '<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6"/><path d="M9 13h8M9 17h6"/>',
    "arxiv": '<path d="M4 4l16 16M20 4L4 20"/>',
    "code": '<path d="M8 6l-6 6 6 6M16 6l6 6-6 6"/>',
    "github": '<path d="M9 19c-4 1.5-4-2-6-2.5M15 21v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1-.3-3.4 1.3a11.7 11.7 0 0 0-6.2 0C6.6 2.8 5.6 3.1 5.6 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4.2 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/>',
    "video": '<rect x="2" y="5" width="14" height="14" rx="2"/><path d="M16 10l6-3v10l-6-3z"/>',
    "data": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "quote": '<path d="M7 7h4v4c0 3-1.5 5-4 6M15 7h4v4c0 3-1.5 5-4 6"/>',
    "copy": '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
}


def icon(name):
    paths = ICONS.get(name, ICONS["paper"])
    return (
        '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
        'stroke-linejoin="round">' + paths + "</svg>"
    )


def keep_hyphenated(text):
    """Escape text and stop line breaks inside hyphenated words like 'No-Reference'."""
    return re.sub(r"(\S+-\S+)", r'<span class="nowrap">\1</span>', escape(text))


def number(text):
    """Parse a table cell such as '0.758' or '&minus;0.082' for bar widths."""
    try:
        return float(text.replace("&minus;", "-").replace("−", "-"))
    except ValueError:
        return None


class Renderer:
    def __init__(self):
        self.figure_count = 0
        self.table_count = 0

    def p(self, b):
        return "<p>%s</p>" % b["html"]

    def figure(self, b):
        self.figure_count += 1
        size = b.get("size", "wide")
        return (
            '<figure class="figure figure--%s" id="fig-%d">'
            '<img src="%s" alt="%s" loading="lazy" decoding="async">'
            '<figcaption><span class="label">Figure %d.</span> %s</figcaption>'
            "</figure>"
        ) % (escape(size), self.figure_count, escape(b["src"]), escape(b["alt"]),
             self.figure_count, b["caption"])

    def dl(self, b):
        items = "".join(
            "<div><dt>%s</dt><dd>%s</dd></div>" % (escape(i["term"]), i["html"])
            for i in b["items"]
        )
        return '<dl class="terms">%s</dl>' % items

    def facts(self, b):
        items = "".join(
            '<li><span class="fact-value">%s</span> <span class="fact-label">%s</span></li>'
            % (escape(i["value"]), i["label"])
            for i in b["items"]
        )
        return '<ul class="facts">%s</ul>' % items

    def table(self, b):
        self.table_count += 1
        cols = b["columns"]
        bar_col = b.get("bar_column")
        bar_max = float(b.get("bar_max", 1.0))
        head = "".join(
            '<th scope="col"%s>%s</th>' % (' class="num"' if i else "", escape(c))
            for i, c in enumerate(cols)
        )
        body = []
        for g in b["groups"]:
            cls = ' class="is-highlight"' if g.get("highlight") else ""
            rows = []
            if g.get("label"):
                rows.append('<tr class="group"><th colspan="%d" scope="rowgroup">%s</th></tr>'
                            % (len(cols), escape(g["label"])))
            for r in g["rows"]:
                cells = ['<th scope="row">%s</th>' % r[0]]
                for i, cell in enumerate(r[1:], start=1):
                    bar = ""
                    if i == bar_col:
                        v = number(cell)
                        if v is not None:
                            w = max(0.0, min(v / bar_max, 1.0)) * 100
                            bar = '<span class="bar" style="--w:%.1f%%" aria-hidden="true"></span>' % w
                    cells.append('<td class="num">%s%s</td>' % (bar, cell))
                rows.append("<tr>%s</tr>" % "".join(cells))
            body.append("<tbody%s>%s</tbody>" % (cls, "".join(rows)))
        return (
            '<figure class="table-figure" id="tab-%d">'
            '<div class="table-scroll"><table><thead><tr>%s</tr></thead>%s</table></div>'
            '<figcaption><span class="label">Table %d.</span> %s</figcaption></figure>'
        ) % (self.table_count, head, "".join(body), self.table_count, b["caption"])

    def bibtex(self, b):
        return (
            '<div class="bibtex"><pre><code id="bibtex">%s</code></pre>'
            '<button type="button" class="copy" data-copy="bibtex">%s<span>Copy BibTeX</span></button></div>'
        ) % (escape(b["text"]), icon("copy"))

    def block(self, b):
        fn = getattr(self, b["type"], None)
        if fn is None:
            raise SystemExit("Unknown block type: %r" % b["type"])
        return fn(b)


def render(data):
    site, paper = data["site"], data["paper"]
    r = Renderer()

    multi_affil = len(paper["affiliations"]) > 1
    authors = []
    for a in paper["authors"]:
        name = escape(a["name"])
        if a.get("url"):
            name = '<a href="%s">%s</a>' % (escape(a["url"]), name)
        sup = ""
        if multi_affil:
            sup = "<sup>%s</sup>" % ",".join(str(i) for i in a.get("affiliations", []))
        mark = "<sup>*</sup>" if a.get("equal") else ""
        authors.append('<li>%s%s%s</li>' % (name, sup, mark))
    affils = "".join(
        "<li>%s%s</li>" % ("<sup>%d</sup>" % (i + 1) if multi_affil else "", escape(x))
        for i, x in enumerate(paper["affiliations"])
    )
    links = "".join(
        '<li><a class="button" href="%s"%s>%s<span>%s</span></a></li>'
        % (escape(l["url"]),
           "" if l["url"].startswith("#") else ' target="_blank" rel="noopener noreferrer"',
           icon(l.get("icon", "paper")), escape(l["label"]))
        for l in paper.get("links", [])
    )

    nav = "".join(
        '<li><a href="#%s">%s</a></li>' % (escape(s["id"]), escape(s.get("nav", s["title"])))
        for s in data["sections"]
    )
    sections = "".join(
        '<section id="%s" aria-labelledby="%s-h"><h2 id="%s-h">%s</h2>%s</section>'
        % (escape(s["id"]), escape(s["id"]), escape(s["id"]), escape(s["title"]),
           "".join(r.block(b) for b in s["blocks"]))
        for s in data["sections"]
    )

    title = paper["title"]
    head_title = title + (" | " + paper["venue"] if paper.get("venue") else "")
    url = site.get("url", "")
    og_image = url + site["og_image"] if site.get("og_image") else ""
    tldr = '<p class="tldr">%s</p>' % paper["tldr"] if paper.get("tldr") else ""
    venue = '<span class="venue">%s</span>' % escape(paper["venue"]) if paper.get("venue") else ""

    meta = [
        '<meta name="description" content="%s">' % escape(site["description"]),
        '<meta name="theme-color" content="%s">' % escape(site.get("accent", "#1f5f8b")),
        '<meta property="og:type" content="article">',
        '<meta property="og:title" content="%s">' % escape(title),
        '<meta property="og:description" content="%s">' % escape(site["description"]),
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="citation_title" content="%s">' % escape(title),
    ]
    if url:
        meta.append('<meta property="og:url" content="%s">' % escape(url))
    if og_image:
        meta.append('<meta property="og:image" content="%s">' % escape(og_image))
    for a in paper["authors"]:
        meta.append('<meta name="citation_author" content="%s">' % escape(a["name"]))
    if paper.get("venue"):
        meta.append('<meta name="citation_conference_title" content="%s">' % escape(paper["venue"]))

    return TEMPLATE.format(
        lang=escape(site.get("lang", "en")),
        head_title=escape(head_title),
        meta="\n  ".join(meta),
        accent=escape(site.get("accent", "#1f5f8b")),
        title=keep_hyphenated(title),
        footer_title=escape(title),
        venue=venue,
        authors="".join(authors),
        affils=affils,
        links=links,
        tldr=tldr,
        nav=nav,
        sections=sections,
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{head_title}</title>
  {meta}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/style.css">
  <style>:root {{ --accent-base: {accent}; }}</style>
  <script defer src="assets/site.js"></script>
</head>
<body id="top">
  <a class="skip" href="#main">Skip to content</a>
  <header class="masthead">
    <div class="wrap">
      <h1>{title}</h1>
      <ul class="authors">{authors}</ul>
      <div class="byline">{venue}<ul class="affils">{affils}</ul></div>
      <ul class="links">{links}</ul>
      {tldr}
    </div>
  </header>
  <nav class="toc" aria-label="Sections">
    <div class="wrap"><ul>{nav}</ul></div>
  </nav>
  <main id="main" class="wrap">
    {sections}
  </main>
  <footer class="footer">
    <div class="wrap">
      <p>{footer_title}</p>
      <p><a href="#top">Back to top</a></p>
    </div>
  </footer>
</body>
</html>
"""


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "project.json"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "index.html"
    data = json.loads(src.read_text(encoding="utf-8"))
    out.write_text(render(data), encoding="utf-8")
    print("Wrote %s" % out)


if __name__ == "__main__":
    main()

# MAIQ - Project Page

Static project page for **MAIQ: Mask-Aware No-Reference Image Quality Assessment for Inpainting** (WACV 2027).

The page is generated from a single content file, so the same package can be reused for other papers.

## Layout

```text
project.json        page content (title, authors, links, sections)
build.py            renders project.json into index.html (Python 3.9+, standard library only)
index.html          generated page, committed so GitHub Pages can serve it directly
assets/style.css    styles; colors are CSS variables, light and dark themes included
assets/site.js      BibTeX copy button and current-section highlighting
assets/images/      figures
.nojekyll           tells GitHub Pages to serve files as-is
```

## Editing

1. Edit `project.json` and put figures in `assets/images/`.
2. Run `python3 build.py`.
3. Preview with `python3 -m http.server 8000` and open `http://localhost:8000`.
4. Commit `project.json`, `index.html`, and any new images.

Do not edit `index.html` by hand; it is overwritten by `build.py`.

## project.json

`site` sets the public URL, the accent color (`accent`), the social preview image, and the meta description.

`paper` holds the title, `venue`, `authors` (each with `affiliations` indices and an optional `url`), `affiliations`, header `links`, and an optional one-paragraph `tldr`. Link icons: `paper`, `arxiv`, `code`, `github`, `video`, `data`, `quote`.

`sections` is the page body. Each section has an `id`, a `title` (also used in the section navigation, or set `nav` for a shorter label), and a list of `blocks`:

| type | fields | renders as |
|---|---|---|
| `p` | `html` | paragraph |
| `figure` | `src`, `alt`, `caption`, `size` (`wide` or `narrow`) | numbered figure |
| `dl` | `items`: `term`, `html` | list of named components |
| `facts` | `items`: `value`, `label` | short list of key numbers |
| `table` | `caption`, `columns`, `groups` (`label`, `rows`, `highlight`), optional `bar_column`, `bar_max` | numbered table with optional inline bars |
| `bibtex` | `text` | BibTeX block with a copy button |

`html` fields, captions, `facts` labels, `tldr`, and table cells are inserted as HTML, so inline tags such as `<strong>` and entities such as `&ndash;` work. Everything else is escaped.

## Deployment

Enable GitHub Pages in the repository settings and deploy from the `main` branch root. The repository must be public on a free organization plan.

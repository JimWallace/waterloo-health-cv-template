# My CV

A University of Waterloo Faculty of Health CV, built from
[waterloo-health-cv-template](https://github.com/JimWallace/waterloo-health-cv-template).
It starts as a fictional CV (Robin Quill): replace it with your own.

One source, two PDFs: `main.tex` compiles to the Faculty of Health CV, and
`apr.tex` to the APR version, with review-period items coloured as teaching,
research, service or awards.

| File | What it holds |
|---|---|
| `cv.toml` | Your name, GitHub login, publication ids, and the template release in use. |
| `main.tex` | The CV: headings, hand-written sections, which publications print under which heading. |
| `scholar.bib` | Publications, talks and software. |
| `grants.bib`, `supervision.bib`, `awards.bib`, `service.bib`, `activities.bib`, `courses.bib`, `committees.bib` | The other records, printed sorted and highlighted from their dates. |
| `apr.tex` | Two lines: `main.tex` in the APR version. Never put content here. |
| `apr-formatting.tex` | Your APR settings (highlight strength and style). |
| `data/trainees.yaml` | Trainees beyond `supervision.bib`, for the `*` marks. |
| `template/` | A copy of a template release. Don't edit it; update it (below). |
| `CLAUDE.md`, `.claude/` | Conventions, plus Claude Code agents and skills that add and verify CV items. |
| `scripts/`, `.github/` | The checker and the GitHub Actions: build, release, template updates, Overleaf. |

## Build

```bash
latexmk main.tex && latexmk apr.tex
```

This needs LuaLaTeX and TeX Live 2025 or newer. On Overleaf, set Menu → Compiler →
LuaLaTeX and, for the APR version, Main document → `apr.tex`.

```bash
python3 scripts/check_cv.py
```

The checker covers duplicate keys, entries that don't print, trainee marks, award
badges, record fields, and the APR lists. CI runs it on every PR.

## Make it yours

1. In `cv.toml`, fill in your name (as it appears in bold in the `.bib` files), family name,
   GitHub login and PDF name, plus your DBLP id, ORCID and OpenAlex id if you have them.
2. Replace the content of `main.tex` and the `.bib` files, keeping the structure. Field
   documentation is in `template/uwhealthcv.dbx`, and the commands are in `template/README.md`.
3. In `CLAUDE.md`, adjust the conventions to your own decisions (it is written in your voice).
4. Push to GitHub and do the one-time setup in `AUTOMATION.md`.

## Template updates

```bash
sh scripts/update_template.sh latest
```

This replaces `template/` with the newest release and records the version in `cv.toml`.
The "Template update" workflow does the same weekly, as a pull request.

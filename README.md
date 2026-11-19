# Waterloo Faculty of Health CV template (with APR highlighting)

A LaTeX template for the University of Waterloo Faculty of Health CV format. One
source compiles to the plain CV and to an APR (Annual Performance Review)
version that colours review-period items as teaching, research, service or
awards. Grants, students, awards, service and courses are biblatex records, so
they print sorted and are highlighted from their dates. The PDFs are tagged
(PDF/UA-2) and archival (PDF/A-4f).

The repository has two parts:

- **The template** (this directory): the LaTeX package `uwhealthcv` and
  `example/`, a fictional CV that uses every feature. No one's personal data.
- **[`starter/`](starter/)**: a complete CV repository to start from: a fictional
  CV split into `.bib` files, a checker for the CV's conventions, Claude Code
  agents and skills that add and verify CV items, and GitHub Actions that build
  both PDFs, publish them as a release, pull in new template releases, and
  optionally mirror to Overleaf. See [`starter/README.md`](starter/README.md).

## Quick start

```bash
git clone https://github.com/JimWallace/waterloo-health-cv-template
sh waterloo-health-cv-template/new-cv.sh my-cv
```

`my-cv/` is then a git repository holding the starter and the latest template
release in `my-cv/template/`. Put your details in `cv.toml`, replace the
fictional content, and push it to a new GitHub repository (or upload it to
Overleaf, compiler LuaLaTeX). Without git, copy `starter/` and put this
directory's files (all but `starter/`) in its `template/`.

## What is here

| File | Role |
|---|---|
| `uwhealthcv.sty` | The only package a CV loads. Reads the files below in the right order. |
| `uwhealthcv-pdfa.tex` | Makes the PDF accessible (tagged, PDF/UA-2) and archival (PDF/A-4f). A CV inputs it before `\documentclass`; see below. |
| `NSERC-formatting.tex` | Page, fonts, header and table setup. |
| `biblatex-formatting.tex` | biblatex tweaks: badge icons in the margin, the `inproceedings` driver. |
| `ACM-Reference-Format.{bbx,cbx,dbx,bst}` | ACM bibliography style (vendored). |
| `aprcv.sty` | APR highlighting. Its header documents every command. |
| `cv-records.tex` | Grants, supervision, awards, service and courses as biblatex records: the tables, the lists, sorting and highlighting. |
| `uwhealthcv.dbx` | The biblatex data model for `@grant`, `@supervision`, `@award`, `@service` and `@course` (fields documented in its header). |
| `cv-layout.tex` | Page-break rules: `\keepwithnext`, `\sectionbreak`, widow and club control. |
| `images/` | Badge images a bib entry can show in the margin with `icon = {images/<file>}`. `icon = {award}` draws the award rosette instead (`biblatex-formatting.tex`); in the APR version it is filled with the award colour when the entry is in the review period. |
| `example/` | A fictional CV that uses every feature. Build it to test a template change. |

## Using it

A CV directory holds the content, keeps this template in `template/`, and puts
it on TeX's search path with a `latexmkrc`:

```perl
ensure_path('TEXINPUTS', './template//');
```

latexmk, Overleaf and the GitHub Actions LaTeX build all read that file. Its
`$pdf_mode = 4;` line selects LuaLaTeX, the engine the template is built
with; on Overleaf, also set Menu → Compiler → LuaLaTeX.

The CV's main file:

```latex
\input{uwhealthcv-pdfa}
\documentclass[12pt]{article}
\usepackage{uwhealthcv}
\addbibresource{mycv.bib}
\setreviewperiod{2025}{2026}
\cvowner{Your Name}
% \DeclareBibliographyCategory and \addtocategory lists for each heading
\begin{document}
...
\end{document}
```

The first line makes the PDF accessible and archival: a tagged PDF/UA-2 file
(screen readers get headings, lists, tables, links and alternative text) that
is also PDF/A-4f (fonts embedded, an sRGB colour profile, XMP metadata with the
title and author from `\cvowner`). The LaTeX kernel only accepts that before
`\documentclass`, so it cannot live in `uwhealthcv.sty`. Tagging needs
LuaLaTeX and TeX Live 2025 or newer (this repository uses TeX Live 2026); leave
the line out for a plain, untagged PDF. CI checks the result
with veraPDF (`starter/scripts/check_pdfa.sh`), which tests what a machine can; it
cannot tell whether alternative text is good.

In the tagged PDF, `\cvsection` is a level-1 heading and `\cvsubheading` a
level-2 heading, even when text follows on the same line; every table's first
row is its column headings; the APR markers and award badges are decorative
artifacts. A figure drawn with TikZ or pgfplots needs alternative text: give
the picture `[cv/alt={…}]`. `[cv/decorative]` marks a picture as decoration.
Both keys do nothing in an untagged build.

The APR version is a two-line file next to it:

```latex
\PassOptionsToPackage{apr}{aprcv}
\input{main}
```

A CV can also provide `apr-formatting.tex` beside its main file. `aprcv.sty`
reads it in the APR version only, after the rest of the template, so it can
change settings such as `\sethighlightstrength` and `\sethighlightstyle`
without affecting the plain CV.

## Interface

These are the names a CV relies on. Changing one is a breaking change for
every CV that uses the template.

- Package: `uwhealthcv` (options `apr`, `plain`), `aprcv` (options `apr`, `plain`).
- Commands: `\setreviewperiod`, `\hlteaching`, `\hlresearch`, `\hlservice`,
  `\hlaward`, `\hlboth`, `\hl…row`, `\aprsample`, `\aprlinemark`, `\ifAPR`,
  `\sethighlightstrength`, `\sethighlightstyle`, `\keepwithnext`,
  `\sectionbreak`, `\usvardate`, `\monthyear`, `\extlink`.
- Section markup: `\cvsection`, `\cvsubheading`, `cvlist` and `cvbulletlist` with `\cvitem`, `cvgroup`, `cvparts`
  with `\cvpart`, `\printcategory`. Documented in the `uwhealthcv.sty` header.
- Records: `\cvowner`, `\printgrants`, `\printsupervision{degree}`, `\printawards`,
  `\printservice{level}`, `\printcourses[scp]` (with `\cvcoursescplabel` and
  `\cvcourseaveragelabel` for its score headings), the entry types `@grant`, `@supervision`,
  `@award`, `@service` and `@course` with the fields in `uwhealthcv.dbx`, and `\me` inside a
  grant's `investigators`. Documented in `cv-records.tex`.
- For other record types: `\aprtypecategory{type}{colour}`, `\aprsetentrycolour`, `\aprentrymark`
  and `\aprmarkleftof{label}`
  (`aprcv.sty`).
- biblatex categories: `aprteaching`, `aprservice`, `apraward`, `aprnone`,
  `aprinclude`, `apralsoteaching`, `apralsoresearch`, `apralsoservice`,
  `apralsoaward`.
- Bib field: `icon` (an image path, or `award` for the rosette).
- File the template reads from the CV: `apr-formatting.tex` (optional).
- File a CV inputs before `\documentclass`: `uwhealthcv-pdfa.tex` (optional).
- TikZ keys: `cv/alt={text}`, `cv/decorative` (`uwhealthcv.sty`).

## Building the example

```bash
cd example
latexmk example.tex
latexmk example-apr.tex
```

CI builds both on every pull request.

## Versions and updates

Releases are git tags (`v0.1.0`) with notes in [`CHANGELOG.md`](CHANGELOG.md).
The version follows the interface above: a new command or option is a minor
release, a fix a patch, and renaming or removing anything in the interface a new
major version. Before 1.0 the interface is still settling, so a minor release
(0.1 → 0.2) may rename or remove something; its CHANGELOG entry says what a CV
must change. `\ProvidesPackage` in `uwhealthcv.sty` and `aprcv.sty` carries
the same version.

A CV keeps a copy of a release in `template/`, because Overleaf cannot use git
submodules. `sh scripts/update_template.sh latest` in the starter replaces it
with the newest release and records the version in `cv.toml`; the starter's
"Template update" workflow does that weekly and opens a pull request, which the
CV's build checks before it merges.

The package may go to CTAN once the interface is stable. A local `template/`
copy will still take precedence over an installed version, so a CV can stay on
any release it likes.

## Licence

LaTeX Project Public License 1.3c ([`LICENSE`](LICENSE)), except the vendored
ACM bibliography style: `ACM-Reference-Format.{bbx,cbx,dbx}` come from ACM's
`acmart` package (LPPL 1.3c) and `ACM-Reference-Format.bst` is public domain, as
its header says.

## Citing

GitHub's "Cite this repository" button reads [`CITATION.cff`](CITATION.cff).

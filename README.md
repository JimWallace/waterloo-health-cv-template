# Waterloo Faculty of Health CV template

**Your CV in the [University of Waterloo Faculty of Health CV format](https://uwaterloo.ca/health/faculty-staff/curriculum-vitae), from one LaTeX source, with the APR version built in and, if you want it, an AI assistant that keeps it up to date.**

The Faculty publishes its CV format as a Word document. This template typesets
that format in LaTeX, and from the same source it also builds the version you
submit for the Annual Performance Review (APR), with every review-period item
highlighted as teaching, research, service or an award. You keep one file, not
two.

![The same CV source compiled twice: the Faculty of Health CV on the left, and the APR version on the right, with review-period publications highlighted green as research and, in the margin, a row of three dots per entry (research, teaching, service) filled for its categories: green alone for a paper, green and yellow for a trainee-authored paper and for teaching software.](docs/images/plain-vs-apr.png)

*Left: `main.tex`, the Faculty of Health CV. Right: `apr.tex`, the same content as
the APR version, in the dots style (the default). All the examples here are
fictional.*

## The APR version

The APR guidelines judge teaching, research and service separately, over a
two-year review period. The APR version shows the reviewer where each item belongs:

- **Highlighting from dates, not by hand.** Set the period once
  (`\setreviewperiod{2025}{2026}`). Papers, talks, grants, students, service roles,
  awards and courses from that period are highlighted automatically. When the
  period moves, the highlighting moves with it.
- **Two colours when work counts twice.** A paper with a trainee co-author is
  research *and* supervision, and is marked in both colours. Software built
  for teaching can be teaching first and research second. You choose an entry's
  colours with biblatex categories (`aprteaching`, `apralsoresearch`, …).
- **Award badges.** A paper or poster that won an award gets a rosette in the
  margin, filled with the award colour when the entry is in the review period.
- **APR-only content.** Wrap a section in `\ifAPR … \fi` and it appears only in
  the APR version. Use it for notes to the committee, such as how to read
  authorship order in your field, or for course evaluation scores.
- **Your choice of style.** Entries in two colours can be shown as a bar,
  halves, a split, a blend or dots, and the highlight strength is adjustable
  (`apr-formatting.tex`). The default is dots: each highlighted entry gets
  three dots in the margin (research, teaching, service), filled for the
  categories it counts in, so two-colour work reads at a glance and survives
  black-and-white printing as filled versus empty. An entry in two `apralso…`
  lists counts in three categories; the dots style fills all three (the other
  styles show two).

![Publications in the APR version in the dots style: a review-period journal article highlighted green with the research and teaching dots filled for its trainee co-author, an empty award rosette beside an older paper, and a trainee's award-winning poster with a filled pink rosette before its dots.](docs/images/apr-publications.png)

Grants, students, service, awards and courses are records in `.bib` files, not
hand-made tables. They print sorted, in the Faculty's table layouts, and are
highlighted from their dates: a grant whose tenure overlaps the period, a
student still in progress, a committee you sat on, a course you taught. The
APR version adds your course evaluation scores beside the school averages.

![Grants, supervision, service and courses in the APR version in the dots style: an active grant highlighted as research, current and recently graduated students as teaching, a Faculty committee as service, a General Chair role with both the service and research dots filled, and a course from the review period with its evaluation scores and the school average.](docs/images/apr-records.png)

The PDFs are tagged (PDF/UA-2, so screen readers get headings, lists and
tables) and archival (PDF/A-4f).

## A CV that keeps itself up to date

Most of the effort of a CV is keeping it current: the paper accepted in March,
the DOI that appears in June, the review recognition, the PC you joined, the
student who defended. [`starter/`](starter/) is a complete CV repository that
hands that work to [Claude Code](https://claude.com/claude-code) agents and
checks everything they do.

- **Weekly update from your inbox and calendar.** A scheduled Claude task, given
  your Microsoft 365 (Outlook) connector, reads the past week's mail and calendar
  for acceptances, review recognitions, program-committee and editorial roles,
  invited talks and thesis examinations. It also checks DBLP, Crossref and
  OpenAlex for new publications and missing DOIs. It drafts the entries and opens
  a pull request. Rejections, invitations still pending and anything else private
  never reach the repository; they go only in the task's report to you
  ([`starter/AUTOMATION.md`](starter/AUTOMATION.md),
  [`starter/automation/weekly-update.md`](starter/automation/weekly-update.md)).
- **Tell it in a sentence.** Open an issue ("CHI 2027 paper accepted with my PhD
  student …") and the next weekly run adds it as a pull request. With a Claude
  token in the repository's secrets, mentioning `@claude` in the issue does it
  right away.
- **Every change is verified independently.** Before a pull request is labelled
  for merging, separate sub-agents re-check it from scratch. They check citations
  against Crossref, DBLP and the publisher; trainee marks against your roster;
  the heading and APR colour; figures; and the whole diff against the change
  list ([`starter/.claude/agents/`](starter/.claude/agents/)). A deterministic
  checker (`scripts/check_cv.py`) and a warning ratchet run in CI on every
  change.
- **You stay in charge.** The assistant never invents a bibliographic fact,
  never adds a trainee or rewrites an existing entry on its own, and never edits
  your narrative. It asks instead, in a "Questions for the owner" list on the
  pull request. Routine verified additions can merge themselves; everything else
  waits for you.
- **Builds and releases.** GitHub Actions compile both PDFs on every change,
  publish the latest pair as a release, open a pull request when a new template
  release comes out, and can mirror the repository to Overleaf.

The template works without any of this: the LaTeX package needs nothing but a TeX
installation or Overleaf.

## Quick start

```bash
git clone https://github.com/JimWallace/waterloo-health-cv-template
sh waterloo-health-cv-template/new-cv.sh my-cv
```

`my-cv/` is then a git repository holding the starter, with the latest template
release in `my-cv/template/`. Next:

1. Put your name, GitHub login and publication ids (DBLP, ORCID) in `cv.toml`.
2. Replace the fictional content of `main.tex` and the `.bib` files.
3. Build with `latexmk main.tex && latexmk apr.tex` (LuaLaTeX, TeX Live 2025 or
   newer), or upload the folder to Overleaf and set the compiler to LuaLaTeX.
4. To turn on the automation, push to a new GitHub repository and follow
   [`starter/AUTOMATION.md`](starter/AUTOMATION.md).

Without git, copy `starter/` and put this repository's files (everything except
`starter/`, `docs/`, `.github/` and `new-cv.sh`) in its `template/` folder.

## How it is organized

- **The template** (the root of this repository) is the LaTeX package
  `uwhealthcv`, plus `example/`, a fictional CV that uses every feature. It holds
  the format only, never anyone's content.
- **[`starter/`](starter/)** is a CV repository built on it. A CV keeps a copy of
  a template release in its `template/` folder (Overleaf can't use git
  submodules) and updates it with `sh scripts/update_template.sh latest`. A
  weekly workflow does that for you as a pull request. Format and content stay
  separate, and new template features reach every CV without any copying by hand.

The rest of this file is the reference for the package.

## What is here

| File | Role |
|---|---|
| `uwhealthcv.sty` | The only package a CV loads. Reads the files below in the right order. |
| `uwhealthcv-pdfa.tex` | Makes the PDF accessible (tagged, PDF/UA-2) and archival (PDF/A-4f). A CV inputs it before `\documentclass`; see below. |
| `NSERC-formatting.tex` | Page, fonts, header and table setup. |
| `biblatex-formatting.tex` | biblatex tweaks: badge icons in the margin, the `inproceedings` driver. |
| `ACM-Reference-Format.{bbx,cbx,dbx,bst}` | ACM bibliography style (vendored). |
| `aprcv.sty` | APR highlighting. Its header documents every command. |
| `cv-records.tex` | Grants, supervision, committees, awards, service and courses as biblatex records: the tables, the lists, sorting and highlighting. |
| `uwhealthcv.dbx` | The biblatex data model for `@grant`, `@supervision`, `@committee`, `@award`, `@service` and `@course` (fields documented in its header). |
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
\documentclass[11pt]{article}
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
  with `\cvpart` (bold title) and `\cvpart*` (plain title), `\printcategory`. Documented in the `uwhealthcv.sty` header.
  The indents and blank lines follow the Faculty of Health's vitae format (the
  `.doc` linked from uwaterloo.ca/health/faculty-staff/curriculum-vitae): a
  part's letter at 0.25in, its title and all list content at 0.5in, one blank
  line after a section heading and between parts, none between a part's title
  and its content. The lengths `\cvletterindent`, `\cvcontentindent` and
  `\cvdegreelabelwidth` set the grid.
- Records: `\cvowner` (the name, set once) and `\cvname` (prints it), `\printgrants` and `\printgrants[status]`, `\printsupervision{degree}`,
  `\printcommitteecounts{groups}`, `\printcommittees[period]{group}`,
  `\cvcommitteegroup{group}{degrees}`, `\printawards` and `\printawards[level]`,
  `\printservice{level}`, `\printcourses[scp]` (with `\cvcoursescplabel` and
  `\cvcourseaveragelabel` for its score headings), the entry types `@grant`, `@supervision`,
  `@committee`, `@award`, `@service` and `@course` with the fields in `uwhealthcv.dbx`, and `\me` inside a
  grant's `investigators`. Documented in `cv-records.tex`.
- For other record types: `\aprtypecategory{type}{colour}`, `\aprsetentrycolour`, `\aprentrymark`
  (`aprcv.sty`). `\aprmarkleftof{label}` is still accepted but does nothing
  since v0.5.1: every marker sits in one column left of the text block.
- biblatex categories: `aprteaching`, `aprservice`, `apraward`, `aprnone`,
  `aprinclude`, `apralsoteaching`, `apralsoresearch`, `apralsoservice`,
  `apralsoaward`.
- Per-entry detail line: `\setentrydetail{key}{text}` (`biblatex-formatting.tex`).
- Generated numbers: `\setcvnumber{name}{value}` and `\cvnumber{name}` (`uwhealthcv.sty`),
  for counts a script writes from the record and the CV's sentences print.
- Missing data (`uwhealthcv.sty`): the `gaps` option, or `\def\cvshowgaps{}` before the
  package loads, makes a review copy that marks missing data in orange (`CVgap`,
  `CVgapText`); `\setentrygap{key}{text}` names what an entry lacks, and `\cvgap{text}`
  marks a spot in running text. Without it they print nothing. See
  `example/example-gaps.tex`.
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

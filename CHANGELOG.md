# Changelog

Versions follow the interface in `README.md`: minor for additions, patch for
fixes, major for anything renamed or removed (with what a CV must change).

## Unreleased

## v0.12.0 — 2026-11-24

One addition: nothing for a CV to change.

- `\healthmark`: an author mark (‡) for a co-author whose primary
  appointment is in a health, clinical or public health unit, written after
  the family name in the .bib like the trainee `*` and presenter `{\dag}`
  (`Clinician{\healthmark}, Casey`), so a reader outside the field sees
  which collaborators are in health. The example marks one co-author and
  says what the marks mean under PUBLICATIONS.

## v0.11.1 — 2026-11-24

One fix: nothing for a CV to change.

- `\extlink`'s arrow no longer turns into the icon's name
  ("External-Link-Alt") when text is copied from the PDF or extracted
  (`pdftotext`, ATS and indexing tools): the icon carries an empty
  ActualText, in tagged and untagged PDFs. The example's contact block
  now has a link, so CI checks it.

## v0.11.0 — 2026-11-24

One addition: nothing for a CV to change.

- `\setentrytag{key}{text}`: a short tag (e.g. "Top 2%") in the margin left
  of one bibliography entry, kept outside the .bib like `\setentrydetail`
  so a script can regenerate it. It sits under the entry's badge or APR
  dots when it has them, so it reads as part of the marker, and otherwise
  on the entry's first line, 8pt left of its label (measured per entry, so
  [C22] and [C7] get the same gap). Printed in both the plain and the APR
  version; `\cventrytagformat` sets its look (small bold by default).
  Shown in the example.

## v0.10.0 — 2026-11-22

Additions: nothing for a CV to change.

- Generated numbers. `\setcvnumber{name}{value}` defines a number (a count
  a script writes from the record, such as the papers in the review period
  a trainee led) and `\cvnumber{name}` prints it, so a sentence the owner
  wrote stays true as the record grows. An undefined name prints a bold
  **??** and a warning. A CV that defined these itself with
  `\providecommand` keeps working, and its definitions give way to these.
  The example's APR note uses one.
- A review copy that marks missing data. With the `gaps` option (or
  `\def\cvshowgaps{}` before the package loads, as
  `example/example-gaps.tex` does), missing data prints in orange, a colour
  none of the APR highlights use: `\setentrygap{key}{text}` adds
  "Missing: text" under any entry (publications and every record type),
  `\cvgap{text}` marks a spot in running text, and a grant's blank amount,
  tenure, agency, title or role and an undefined `\cvnumber` are marked
  without being asked. Without the option nothing changes, so a CV can keep
  its gap list in the source and build the review copy alongside the plain
  and APR versions.

## v0.9.1 — 2026-11-22

Fixes: nothing for a CV to change.

- A grant with no `amount` (an application whose budget isn't settled yet)
  printed nothing in the CV and stopped the build with a siunitx "Invalid
  number" error. Its amount cell is now blank, like a missing tenure, title
  or role, so `\printgrants[Submitted]` can list an application before all
  its details are known. The example shows one.

## v0.9.0 — 2026-11-22

Additions: nothing for a CV to change.

- Awards can be grouped. An `@award` takes an optional `level` (like
  `@service`; several comma-separated), and `\printawards[research]` prints
  only the awards whose level names it, so a CV can put research awards,
  teaching awards and recognitions under their own headings, or print trainee
  awards under supervision. `\printawards` alone still prints every award.
- Submitted grants. A `@grant` takes an optional `status` (`Submitted`):
  `\printgrants` leaves those out, and `\printgrants[Submitted]` prints them
  in their own table. In the APR version, add a submitted application's key to
  `aprinclude` to highlight it when its proposed tenure starts after the
  review period.
- Start years for students. A `@supervision` takes an optional `started`
  year, printed as `2019 -- 2022` for a completed student and
  `In progress (since 2023)` for a current one.
- The example uses all three.

## v0.8.1 — 2026-11-21

A fix: nothing for a CV to change.

- The plain CV (and the APR styles other than dots) draws an entry's badge
  (the award rosette or an `icon` image) just left of its label, 6pt from it
  and centred on the first line, as the dots style places a rosette with no
  dots, instead of out in the left margin. An entry outside the content
  column keeps it in the margin.

## v0.8.0 — 2026-11-21

An addition: nothing for a CV to change.

- `\cvname` prints the name set with `\cvowner`, so a CV sets its owner's
  name once: `\cvsection{NAME/DATE:} \cvname, \usvardate\today` matches the
  running header, the grants table (`\me`) and the PDF's metadata. The
  example and the starter use it.

## v0.7.0 — 2026-11-21

A change a CV makes: `\documentclass[11pt]{article}` (was 12pt). The
template warns when a CV uses another size.

- The page and type are the Faculty of Health vitae format's (the `.doc`
  linked from its CV page): margins left 1in, right 1.06in, top 0.83in,
  bottom 0.54in, the header 0.5in from the top of the page; 11pt Times (TeX
  Gyre Termes), headings included. Before: 0.75in margins and 12pt.
- The running header is the format's: the candidate's name (`\cvowner`) on
  the left and the date and page number on the right, in bold italic.
- Dots style: an entry that starts in the content column (lists,
  publications, students) has its marker just left of that column, next to
  the entry; one that starts at the text block (a table row) keeps its marker
  at the text block. The rosette now sits about 0.85in from the paper edge.
- Dots style: a rosette with no dots (an award badge on an entry outside the
  review period) sits where the dots would be, next to the entry, instead of
  in the slot to their left.

## v0.6.0 — 2026-11-21

An addition and fixes: nothing for a CV to change, though a CV can drop the
`\\` and blank lines it used for spacing (see below), and can use `\cvpart*`
for the format's plain part titles.

- Indents follow the Faculty of Health's vitae format (the `.doc` linked from
  its CV page): a part's letter (a), b) ...) at 0.25in, its title and every
  list's content at 0.5in. Before, lists sat at about 0.41in and part titles
  at 0.39in. A list inside a part starts at the part's title instead of being
  indented again.
- Supervision degree labels (PhD, MSc, MMath ...) are left-aligned in the
  content column, in a label column as wide as "MMath"
  (`\cvdegreelabelwidth`), so every degree's students start at the same place.
  `cvgroup` uses the same column.
- Vertical spacing follows the format too: one blank line after a section
  heading and between parts, labelled lists and degree groups; a part's title
  or a `\cvsubheading` label is followed directly by its content. Lists no
  longer add their own top spacing, which had made the gaps vary from section
  to section. A `\\` straight after `\cvpart{...}` is dropped, so
  `\cvpart{Invited} \\` no longer leaves an empty line.
- `\cvpart*{Title}` gives a part a plain title, as the format sets the parts of
  PRESENTATION TO SCHOLARLY GROUPS and SERVICE.
- Example and starter: PRESENTATION TO SCHOLARLY GROUPS has its colon and plain
  part titles; SERVICE is in lettered parts; the committee counts are under
  GRADUATE STUDENT SUPERVISION as b) As Committee Member, as in the format; the
  DEGREES RECEIVED table starts at 0.5in, directly under its heading.
- A URL in a bibliography entry no longer spreads out on a justified line
  ("https : / / example . org"): its break points don't stretch
  (`\biburlbigskip`), so the line's word spaces take up the slack.
- Dots style: every entry's marker now sits in one column, right-aligned
  against the left edge of the text block. Before, numbered publications put
  theirs left of the [J1] label, supervision lists left of each degree label
  (so PhD, MSc and MMath each had their own column), plain lists 0.45in from
  the paper edge, and table rows at the text block, so a page could show four
  or five columns. The rule that keeps the marker off the paper edge now keeps
  only the dots 0.25in clear, so a rosette doesn't push its dots out of the
  column; at the Faculty's 0.75in margins the rosette sits about 0.1in from
  the edge. `\aprmarkleftof` does nothing now (kept so a CV that calls it
  still compiles). The README screenshots show the new column.

## v0.5.0 — 2026-11-20

An addition: nothing for a CV to change.

- An entry can have three colours: put it in two `apralso…` categories (for
  example `aprservice` plus `apralsoteaching` and `apralsoresearch`). The dots
  style fills all three dots; the other styles show the primary colour and
  the later of the two in the order teaching, research, service, award, which
  is the colour they showed before. Table rows (`\aprentrymark`) carry the
  third colour too. The example's meetup shows it. Nothing for a CV to change.

## v0.4.3 — 2026-11-20

A fix: nothing for a CV to change.

- `CITATION.cff` gives the current version and release date (it still said
  0.1.0), so a citation of the template, or an archived copy of a release,
  names the right version.

## v0.4.2 — 2026-11-19

A fix: nothing for a CV to change.

- `\printcommitteecounts` left out the earliest years when only named
  committees covered them (it took the first year after a committee's
  range was counted). The example now has such a year.

## v0.4.1 — 2026-11-19

Nothing for a CV to change: the dots style is now the example's and the
starter's default, and the README shows it.

- README: the screenshots show the APR version in the dots style, and the text
  and alt text describe the dots.
- The example and the starter use the dots style (`\sethighlightstyle{dots}`
  in `apr-formatting.tex`) instead of the bar. An existing CV keeps its own
  setting.

## v0.4.0 — 2026-11-19

Additions only: nothing for a CV to change.

- `@committee` records for thesis and examination committees, with
  `\printcommitteecounts{MSc, PhD}` (one line per year: "2026 --- 4 MSc,
  6 PhD", counted from the records' dates) and `\printcommittees[period]{PhD}`
  (the named committees as a bulleted list). `\cvcommitteegroup{MSc}{MSc,
  MASc}` counts several degrees together. Count-only records (`count`, no
  author) give a year's number where the committees aren't listed by name.
  Shown in the example; the starter keeps them in `committees.bib`.
- Starter: the Template update workflow opens an issue with a one-click PR link
  when the repository doesn't allow workflows to open pull requests, instead
  of failing.

## v0.3.0 — 2026-11-19

One addition: nothing for a CV to change.

- Release workflow: check CI through the commit's check runs (the run-search
  query missed a passing run).
- `\setentrydetail{key}{text}`: a line of small text under one bibliography
  entry (e.g. a software entry's releases, commits and lines of code), kept
  outside the .bib so a script can regenerate it. Shown in the example.

## v0.2.1 — 2026-11-19

Documentation only: nothing for a CV to change.

- README: what the template and the APR version do, with screenshots from the
  starter CV (`docs/images/`, not copied into a CV's `template/`), and the
  agentic workflow in `starter/`.

## v0.2.0 — 2026-11-19

Changes made in a CV's own copy of the template while v0.1.0 was being split
out, now released here. Additions only: nothing for a CV to change.

- `@supervision`: optional `program` field, printed in parentheses after the
  student's name ("Sam Student (Computer Science), …").
- `@service`: optional `note`, printed under the line in italics.
- `\aprlinemark`: in a highlighted entry, ends the highlight of a line that a
  forced break ends early, so a noted entry's first line stops at its text.
- Release workflow: tags a version and publishes its CHANGELOG section as the
  release notes (Actions → Release).

## v0.1.0 — 2026-11-19

First release as its own repository. Pre-1.0: the interface may still change
in a minor release; the CHANGELOG says what a CV must do when it does.

- `uwhealthcv` package: the Faculty of Health CV format, tagged PDF/UA-2 and
  PDF/A-4f output (`uwhealthcv-pdfa.tex`), section markup, page-break rules.
- `aprcv`: the APR version with review-period highlighting for teaching,
  research, service and awards, two-colour styles and adjustable strength.
- Records for grants, supervision, awards, service and courses (`@grant`,
  `@supervision`, `@award`, `@service`, `@course`), sorted and highlighted
  from their dates.
- `starter/`: a CV repository with the checker, Claude Code agents and skills,
  and GitHub Actions for building, releasing, template updates and Overleaf.

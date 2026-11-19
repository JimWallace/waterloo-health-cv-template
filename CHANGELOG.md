# Changelog

Versions follow the interface in `README.md`: minor for additions, patch for
fixes, major for anything renamed or removed (with what a CV must change).

## Unreleased

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

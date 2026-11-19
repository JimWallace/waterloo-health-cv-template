# Changelog

Versions follow the interface in `README.md`: minor for additions, patch for
fixes, major for anything renamed or removed (with what a CV must change).

## Unreleased

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

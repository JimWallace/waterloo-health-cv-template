# The CV template

This repository is the Faculty of Health CV template (the root) plus `starter/`,
a complete CV repository that uses it (see `README.md`). CVs keep a copy of a
release of the root in their `template/` directory.

- **No personal data here.** No real names, publications, grants, students or
  narrative. The examples use fictional people: Alex Example in `example/`,
  another in `starter/` (`starter/cv.toml`). The starter's CI fails if its `template/`
  contains the owner's family name (`cv.toml`), so the two stay distinct.
- **Keep the example building.** A template change must leave
  `example/example.tex` and `example/example-apr.tex` compiling. If you add a
  feature, show it in the example.
- **The interface in `README.md` is a contract.** Renaming or removing a
  command, option, category or the `icon` field breaks every CV that uses it.
  Do it only when asked, as a new major version (a new minor version before
  1.0), with the change and what a CV
  must do in `CHANGELOG.md`, and update `starter/main.tex` in the same PR.
- **Releases.** Every change adds a line under "Unreleased" in `CHANGELOG.md`.
  A release moves those lines under the new version, sets the same version and
  date in `\ProvidesPackage` (`uwhealthcv.sty`, `aprcv.sty`), and, once CI passes on
  that commit, runs the Release workflow (`.github/workflows/release.yml`), which tags
  `vX.Y.Z` and publishes the release. Claude sessions can't push tags; they start it
  with the GitHub API (workflow dispatch).
- **`starter/` is a CV repository, not part of the package.** Its `CLAUDE.md`,
  agents, skills, scripts and workflows are for the CV that gets made from it;
  `update_template.sh` leaves `starter/`, `.github/` and `new-cv.sh` out of a
  CV's `template/`. Keep it free of anyone's real data and generic: per-person
  settings go in `starter/cv.toml`.
- CI (`.github/workflows/ci.yml`) builds `example/` and the starter CV (plain
  and APR), and runs the starter's checker and tests. A change to either half
  must keep all of that green.
- **Watch TeX's memory.** biber writes a full copy of every entry into the
  `.bbl` for each sorting/refcontext in use, and TeX (5M words of main
  memory in CI's TeX Live) must hold them all. Reuse an existing sorting template where the
  order allows, and don't use `labelprefix` or a new refcontext per heading.
  `grep "words of memory" main.log` shows the usage.

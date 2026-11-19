# My CV

LaTeX CV in the University of Waterloo Faculty of Health format, started from the
waterloo-health-cv-template starter. Who I am (name, DBLP, ORCID) is in `cv.toml`; the
scripts, agents and workflows read it from there. The repo has two halves:

- **The template** (`template/`): the Faculty of Health format and the APR highlighting
  (`uwhealthcv.sty`, `aprcv.sty`, the formatting and page-break files, the ACM biblatex style,
  badge images) plus a fictional example CV. No personal data. It is a copy of a release of
  the template repository (`cv.toml` [template]); never edit it here. To change the format,
  change the template repository; `sh scripts/update_template.sh <tag>` (or the weekly
  "Template update" workflow) brings a new release in. Its `README.md` documents the interface.
- **My CV** (everything else): content and my settings. `latexmkrc` puts `template/` on TeX's
  search path, so `main.tex` just says `\usepackage{uwhealthcv}`.

One source, two PDFs:

- `main.tex` compiles to the plain Faculty of Health CV.
- `apr.tex` compiles `main.tex` with the `apr` option: adds the "A Note on…" sections and colours
  review-period items (see the header of `template/aprcv.sty`). Never put content in `apr.tex`.
- `scholar.bib` holds publications, talks and software. `main.tex` decides which heading each
  entry prints under with `\addtocategory{<category>}{key, key, …}` near the top.
- `grants.bib` holds grants (`@grant`), `supervision.bib` my students (`@supervision`) and
  `awards.bib` the ACADEMIC AWARDS AND DISTINCTIONS list (`@award`) and
  `service.bib` the SERVICE lists and `activities.bib` the SCHOLARLY AND PROFESSIONAL
  ACTIVITIES lists (both `@service`) and `courses.bib` the COURSES TAUGHT table (`@course`).
  The fields are described in `template/uwhealthcv.dbx`. They print sorted, and the APR
  colours come from their dates, so there are no years to keep in step by hand.
- `apr-formatting.tex` holds my settings for the APR version (highlight strength and style).
- My trainees are everyone in `supervision.bib` plus `data/trainees.yaml`, which adds the other
  trainees (undergraduates, RAs) and extra spellings. The checker flags a supervised student
  whose name is spelled differently in the two.

The repo can be mirrored to Overleaf (see `.github/workflows/overleaf-sync.yml` and
`AUTOMATION.md`). GitHub `main` is the source of truth; never force-push `main`.

## Hard rules

1. **Never invent or "fill in" bibliographic facts.** Every author list, title, venue, year,
   pages and DOI must come from a record you retrieved this run (DOI landing page, Crossref,
   DBLP, OpenAlex, ACM DL, publisher page) or from something I wrote in an issue. If a fact
   can't be confirmed, leave it out and say so in the PR.
2. **Never delete or rewrite existing CV content** (entries, table rows, narrative) unless the
   task is explicitly to correct it and the correction is supported by a retrieved record or
   by me. Corrections to existing entries always go in their own commit.
3. **Do not edit the narrative sections** ("A Note on …", inside `\ifAPR … \fi`) in automated
   runs. Suggest changes in the PR description instead.
4. **Trainee marks are my call.** Add `*` only for my trainees (`supervision.bib` or
   `data/trainees.yaml`). Never add a person to either file yourself; ask in the PR ("Is X your trainee?") and label it
   `needs-review`.
5. Keep diffs minimal: no reformatting, re-sorting or whitespace churn in files you touch.

## Conventions

**Bib entries** (`scholar.bib`)
- Key: `familyYYYYfirstword` in lower case, e.g. `student2026example`. Keys must be unique:
  `python3 scripts/check_cv.py` fails on duplicates (biber silently drops the second copy).
- My name is always in bold, exactly as `owner.name` in `cv.toml`: `\textbf{Robin Quill}`.
- Trainee: `*` straight after the family name — `Wong*, Veen` or `Veen Wong*`. Not on the given
  name (`Homaeian, L.*` loses the mark under `giveninits`).
- Presenter of a talk or paper: `{\dag}` after the name (after `*` if both): `Gauthier*{\dag}, Robert P`.
- A paper or talk that won an award: `icon = {award}` (the rosette in the margin; in the APR
  version it is filled pink when the entry is in the review period), the award in bold in
  `note`, e.g. `note = {\textbf{Best Paper Honourable Mention Award}}`, and an `@award` in
  `awards.bib` with `work = {<that key>}`. The checker fails if either half is missing. If a
  trainee won it, add the award's key to `apralsoteaching` too.
- Include `doi` whenever one exists; ACM entries use `@inproceedings` (conference proceedings)
  or `@article` (PACM / journals) as the ACM DL export does.
- Accepted-but-unpublished work: add `note = {To appear}` and no DOI; the weekly run backfills
  the DOI when it appears.
- Refereed work that has no DOI at all (a poster or abstract with no archival proceedings):
  `nodoi = {<reason>}`. It does not print; it tells `check_cv.py` not to ask for a DOI. Only I
  decide that a work has none.

**Acceptance rates and impact factors** (in the entry's `note`, after any text already there,
joined with ". ")
- Conference papers and PACM articles (CSCW, CHI PLAY, GROUP, ISS):
  `Acceptance rate: 25.6\% (64/250)`. Give the counts when the source states them, otherwise
  just the percentage. Use the rate for the paper's own track (full papers, notes, Late-Breaking
  Work, Provocations & WiP…), never the main-track rate for another track.
- Journal articles: `Journal Impact Factor (2025): 4.4`, the latest JCR year. A journal that
  publishes a journal-wide acceptance rate (PLOS ONE) may have both.
- Sources, best first: the decision letter or program chairs' email; the proceedings front
  matter or issue editorial; the conference or publisher site (JMIR, Springer, Elsevier, ACM
  journal pages for JIFs); then my own CVs. Third-party compilations and JIF aggregator sites
  only when nothing better exists and two of them agree; say so in the PR.
- Extended abstracts, posters, demos, workshop papers and companion items usually have no
  rate: record that in `data/metrics.yaml` (`none`) instead of borrowing a rate. When a rate
  or JIF probably exists but can't be found, record it there as `unresolved` with the date.
  `python3 scripts/missing_metrics.py` lists entries with neither (reporting only, not CI).

**Which heading** (`\addtocategory` in `main.tex`; each printed entry in exactly one of these)
- `journal`: journal articles, including Proceedings of the ACM (PACM HCI, CSCW, CHI PLAY,
  GROUP, ISS) and JMIR etc.
- `conference`: full and short papers in conference proceedings (CHI, DIS, GI, CHI EA, LBWs,
  workshop papers published in proceedings).
- `presentations`: self-initiated talks/posters without archival proceedings. `invited`: invited talks.
- `technicalreports`, `other`, `patent`, `software` as named.
- `unprinted`: entries I keep in `scholar.bib` but do not print. Listing a key here records
  that decision, so `check_cv.py` stops warning that it does not appear. Only I add keys.

**APR colours** (`main.tex`, block after the categories; rules in `template/aprcv.sty`)
- Bib entries in the review period (`\setreviewperiod`) are research-green automatically.
  `aprinclude` treats an entry as in the period (e.g. a 2027 paper accepted during it);
  `aprnone` turns highlighting off for one entry. Only I add keys to either.
- If any author is my trainee (`*`) or a trainee presented (`\dag`), also add the key to
  `apralsoteaching`.
- Grants are highlighted when their `date` range overlaps the period; students when they are
  `status = {In progress}` or their `date` is in the period. Nothing to add by hand.
- Awards are highlighted when their year is in the period. Other non-bib items use `\hlteaching[years]{…}`, `\hlresearch`, `\hlservice`, `\hlaward`.
  Always give `[years]`.

**Where non-publication items go**
- Awards → ACADEMIC AWARDS AND DISTINCTIONS (newest first, `\hlaward[YYYY]{…}`).
- Reviewing, PCs, editorial roles, organizing → a `@service` entry in `activities.bib` with `level`
  grantreferee, journal, organizing, programcommittee or referee (the SCHOLARLY AND PROFESSIONAL
  ACTIVITIES lists). A chair role that is also scholarship stays in `service.bib` with
  `level = {discipline, organizing}`, so it prints in both sections. Only the ACM membership
  line of that section is still hand-written in `main.tex`.
- Awards → an `@award` in `awards.bib` (`title` as it should print, `date` = the year,
  `count` for "3 ×" lines). Order within a year follows the file.
- Service → a `@service` entry in `service.bib`: `title` as it prints, `level` (one of the
  `\printservice{…}` lists in `main.tex`: school, faculty, university, discipline) and
  `date = {2023/2025}` for the years served (`2021/` for an ongoing role: "2021 -- Present",
  sorted first). A `level` may name several lists, comma-separated. Optional `years` prints instead of the range
  ("2017, 2019 -- 2021"); optional `role` prints after the years ("General Chair"). The lists
  sort newest first and are highlighted from the dates; a leadership role that is also
  scholarship goes in `apralsoresearch`.
- Grants → a `@grant` entry in `grants.bib`. List investigators in the order given, with
  `\me` for me and `role` for my role; `amount` is digits only; `date = {2026/2028}` is the
  tenure. Order in the file doesn't matter.
- Supervision → a `@supervision` entry in `supervision.bib`: `author = {Family, Given}`,
  `degree` (one of the `\printsupervision{…}` lists in `main.tex`), and `status = {In progress}`
  until they finish, then `date`, `title` and, when I know it, `position`. Committee
  membership and external examining stay as lines in `main.tex`.
- Courses → a `@course` entry in `courses.bib`, one per offering: `course` (EXMP 401/601),
  `title`, `date` = the month the term starts (`2026-01` Winter, `-05` Spring, `-09` Fall),
  optional `level`, `enrolment` and `responses` (digits), `note`, and Student Course Perceptions scores as
  `scp = {Implementation=4.5, Design=4.6}` with the school/department averages in `scpaverage`. The scores
  print only in the APR version. Copy numbers from the SCP report itself; never estimate.

**Teaching, research or service** (the APR colour) follows the Faculty of Health Performance
Review Guidelines and my school's addendum to them, if it has one. Neither is in this repo.
- The review window: tenured members are reviewed every two years, in odd years, on the two
  calendar years before (the 2027 review covers 2025–2026: `\setreviewperiod{2025}{2026}`).
  Teaching and service are judged on those years, scholarship on a two-year window; two
  earlier years are context. Files are due the last working day of December.
- Thesis and comprehensive-exam committees for students I don't supervise are teaching
  ("Teaching and mentorship includes … committees of students (thesis committees,
  comprehensive exams)"), whatever the student's department: `\hlteaching`, counted in the
  "As Committee Member" year line and named in "Committees in the review period".
- Chairing a student's exam (oral comprehensive or defence) is a committee role *and* service
  (the guidelines list the university pool of defence chairs as service). Count it in the
  year line like any committee, and name it under the degree with
  `\hlboth[YYYY]{teaching}{service}{Name (PhD, Program; chair, oral comprehensive examination, YYYY)}`.
- External examining is teaching and service (`\hlboth`), under External Examiner. (The
  Faculty lists "project and oral and thesis examinations/supervision" as teaching.)
- Supervision (graduate, undergraduate thesis, practicum, postdoc) is teaching, but papers and
  grants with trainees are research (with the key in `apralsoteaching` as above).
- Reviewing manuscripts and grants, PCs, societies and organizing are service to the
  profession (`activities.bib`). The Faculty also counts refereeing for journals and granting
  councils, keynotes, society awards and government or professional committees as evidence
  of scholarship, and says a service role such as chairing a curriculum committee or editing
  a journal "may also provide indirect evidence for scholarship or teaching". My standing
  decision: every `activities.bib` entry with level grantreferee, journal, programcommittee or
  referee also goes in `apralsoresearch` (the second list in `main.tex`); add new ones there
  in the same commit. Other second colours are my call.
- Community service related to my scholarship is service to the University; the Faculty also
  counts training such as student mental health training as voluntary service.
- Don't count a work twice across review periods (the guidelines' "reporting integrity"
  rule): a paper counted early through `aprinclude` would be highlighted again by its year in
  the next APR. When the review period moves, list such keys in the PR for me to move to
  `aprnone`. Grants may move from "in submission" to "funded".

**Markup** comes from the template (`template/uwhealthcv.sty`): headings are `\cvsection{…}`,
labels over a list `\cvsubheading{…:}`, list items `\cvitem …` inside `cvlist`, lettered parts
`\cvpart{…}` inside `cvparts` (letters are automatic), students `\item …` inside
`\begin{cvdegree}{PhD}`, bibliography headings `\printcategory[J]{journal}`. Copy the
neighbouring entry; don't write raw `itemize`/`\setlength` blocks.

**Page breaks** are set in `template/cv-layout.tex`. Put `\keepwithnext` before a new heading
that is followed by a list; never use `\newpage` (use `\sectionbreak`).

## Checks

- `python3 scripts/check_cv.py` — deterministic checks; errors fail CI. Run it after every edit.
  Warnings fail too unless `scripts/warnings-baseline.txt` lists them, and a listed warning
  that no longer occurs fails until its line is deleted (`--prune-baseline`). Fix a new warning
  rather than adding it to the baseline: a PR that adds baseline lines cannot auto-merge.
- `python3 scripts/check_cv.py --keys k1,k2` — the same, reporting only on the keys you touched.
- `latexmk main.tex && latexmk apr.tex` (LuaLaTeX, set in `latexmkrc`) — if TeX is installed; CI compiles both anyway.
  Then `python3 scripts/warning_ratchet.py main apr` applies the same baseline to the LaTeX and
  biber warnings (CI does this too, on TeX Live 2026 like Overleaf, and reports what changed in
  the PDF text). A local TeX Live 2023 (Debian) can differ slightly; CI is the reference.
- CI also builds `template/example/` (`example.tex`, `example-apr.tex`) and fails if
  `template/` mentions me (`owner.family` in `cv.toml`).
- Verifier sub-agents in `.claude/agents/` check changes independently. The `cv-verify` skill
  says how to run them.
- `chizen-figures` (`.claude/agents/`) reviews figures with the CHI-Zen plugin's figure
  reviewer and style guide (github.com/JimWallace/CHI-Zen, `plugins/chizen`), plus the CV's
  own overrides. It loads the installed plugin (`.claude/settings.json` enables it for local
  sessions) or clones CHI-Zen in cloud sessions, which don't install plugins. It is one of
  the verifiers: run it whenever a change touches a figure or its data. Data figures are
  pgfplots in `figures/` reading `data/*.csv`. Tables are not reviewed: their layout (underlined headings,
  alignment) is required by the Faculty of Health (AHS) format.

## Pull requests

- The weekly scheduled job follows `automation/weekly-update.md`, works on a branch
  `cv/weekly-YYYY-MM-DD`, and labels its PR either `auto-merge` (every check and verifier
  passed, no open questions) or `needs-review` (plus a "Questions for the owner" section).
  `cv/` PRs merge only with the `auto-merge` label. When unsure, choose `needs-review`.
- Any other PR opened under my GitHub account (`owner.github` in `cv.toml`, or the repo owner) — including one you open for him in a
  chat — merges automatically once CI passes. Open it as a draft, or label it
  `needs-review`, if I should look first.
- Every PR body has a table of the changes (what, where, source).
- `gh pr create` and other GraphQL-based `gh` commands can be blocked in Claude sessions;
  use the REST API (`gh api repos/OWNER/REPO/pulls …`).
- The repo is public: never put email text, rejections, or private details in commits,
  PRs or issues.

## Sources I use

- DBLP person id, ORCID and OpenAlex author id: `cv.toml` [sources] (fill them in).
- Google Scholar can't be queried automatically; don't try.
- The "CV sources" workflow saves DBLP/Crossref records on the `cv-sources` branch weekly
  (`git fetch origin cv-sources`); use them when your session can't reach those sites.

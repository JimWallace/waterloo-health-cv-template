# Weekly CV update — instructions for the scheduled job

The CV owner runs a weekly scheduled Claude task that points here (see `AUTOMATION.md`). Nobody is watching the run: don't
stop to ask. Put questions in the PR (label `needs-review`) and private notes in your final
message. Read `CLAUDE.md` first; its hard rules apply throughout.

The owner asks that the verification in step 5 be done by independent sub-agents.

## 0. Set up

1. Get the CV repository named in the task's prompt (written `OWNER/REPO` below) with push access (attach it if your
   session needs that), clone it, and create the branch `cv/weekly-YYYY-MM-DD` from `main`.
2. GitHub access: use `gh api` (REST). `gh pr create` and other GraphQL-based commands may be
   blocked in Claude sessions; every step below has a REST form.
3. **Records.** `git fetch origin cv-sources` and read, with `git show origin/cv-sources:<path>`:
   `candidates.json`, `records/index.json`, `records/crossref/*.json`, `records/dblp-person.xml`.
   These were fetched by the "CV sources" workflow on GitHub, which can reach DBLP and
   Crossref when your session may not. If `records/index.json` is more than 3 days old or
   missing, start that workflow and wait for it (poll every 30 s, up to 10 min):
   `gh api repos/OWNER/REPO/actions/workflows/cv-sources.yml/dispatches -f ref=main`
   If it still fails, try `python3 scripts/fetch_candidates.py`; if that can't connect either,
   carry on with steps 2–3 and say in the PR that publication sources were unavailable.
4. Run `python3 scripts/check_cv.py --json` for the baseline. Pre-existing warnings are not
   this run's job.

## 1. Follow up last week's PRs

List open PRs from `cv/` branches (`gh api 'repos/OWNER/REPO/pulls?state=open'`).
For each:
- Read the owner's comments on it. Where they have answered a question, apply the answer on that
  PR's branch, push, update the body, and switch the label to `auto-merge` if nothing is left open.
- If its CI failed (`gh api repos/…/commits/<head sha>/check-runs`), fix the cause on its branch.
Don't duplicate an item that is still waiting in an open PR.

## 2. Collect this week's items

a. **Publications** — `candidates.json`: `new` (works not in `scholar.bib`) and `doi_backfill`.

b. **Issues** — open issues labelled `cv-item`:
   `gh api 'repos/OWNER/REPO/issues?labels=cv-item&state=open'`.
   What the owner writes about their own roles, awards, grants and students is a source ("issue #N").

c. **Outlook** — with the Microsoft 365 connector, search the owner's mail since the last weekly
   PR was opened (or the last 8 days). Useful searches, each limited to that window:
   `accepted`, `acceptance`, `camera-ready`, `congratulations`, `decision on your submission`,
   `special recognition`, `outstanding review`, `best paper`, `honourable mention`,
   `program committee`, `associate chair`, `associate editor`, `thank you for reviewing`,
   `agreed to review`, `notice of award`, `funding decision`, `invited talk`, `keynote`,
   `thesis defence`, `examination committee`, `comprehensive exam`.
   Take an item only when an official message (from the venue, journal, agency or university
   office, or the owner's own confirmation) states it outright. If the connector isn't available,
   skip this and say so in your final message.

d. **Calendar** — with the same connector, list the owner's calendar events in the same window.
   Look for talks they gave (invited talks, keynotes, seminars, panels), thesis defences and
   examinations they sat on, and committee or program-committee meetings that show a role.
   A calendar entry alone shows that something was scheduled, not that it happened or what
   their role was: add an item only when a matching email or issue confirms it, or the event
   itself names them as speaker/examiner and its date has passed. Otherwise make it a
   question for the owner. Meeting content, attendees and private appointments stay private.

e. **Missing metrics** — run `python3 scripts/missing_metrics.py`. Take every entry under
   "Missing" (usually papers added since the last run) and the three oldest "Unresolved" ones,
   and look up the acceptance rate or impact factor as `CLAUDE.md` → "Acceptance rates and
   impact factors" says. Check the decision letter in Outlook first (search the venue and year
   with `acceptance rate`, `submissions`, `accepted`), then the front matter, editorial or
   publisher page. Entries the script lists as "Now in scholar.bib" lose their
   `data/metrics.yaml` line.
   **Each July–September** (after Clarivate's June JCR release), also refresh every
   `Journal Impact Factor (YYYY)` note whose year is older than the newest release, from the
   journal's publisher page.

## 3. Triage

For each item keep a one-line reason (it goes in the PR, or in your final message if private).

- **Is it the owner's?** DBLP records come from their disambiguated profile. An OpenAlex/Crossref-only
  record needs the owner's affiliation (`cv.toml`) or a coauthor already on their CV.
- **Already on the CV in another form?** Preprint vs published version, extended abstract vs
  full paper, a changed title: compare authors, venue and year, not just the title. The
  published version of an entry marked "To appear" updates that entry (DOI, pages) instead of
  adding a new one.
- **Final?** Add papers only on final acceptance. Conditional acceptances and revise-and-resubmit
  are not CV items yet: mention them only in your final message.
- **Private — never in the repo, the PR or an issue** (the repo is public): rejections, declined
  or pending invitations, reviewing assignments for specific papers, program committee
  discussions, anything about a student beyond the name and degree that goes on the CV, email
  text, and other people's contact details. Cite an email source only as, for example,
  "acceptance email from CHI 2027 PC chairs, 2026-11-20".
- Skip errata, front matter, proceedings volumes and dataset deposits unless the CV already
  lists that kind of thing.

## 4. Edit

Follow `CLAUDE.md` → Conventions. In short:
- **Bib entries** from the retrieved record (Crossref record from `cv-sources` first, then the
  publisher page): key `familyYYYYfirstword`, the owner's name in bold as `cv.toml` gives it (`\textbf{…}`), `*` only for people
  in `data/trainees.yaml`, `doi` when there is one, `note = {To appear}` when not yet published.
  Add the key to exactly one heading, and to `apralsoteaching` if a trainee is an author and the
  entry is in the review period. Append next to similar entries; don't re-sort.
  A new paper is added with its full information when it is available: DOI, pages, award,
  and its acceptance rate (conference/PACM) or impact factor (journal), usually from the
  acceptance email you found in step 2c. If none can be found yet, add its
  `data/metrics.yaml` line (`none` or `unresolved`).
- **Metrics** (step 2e) → the entry's `note`, as `CLAUDE.md` describes; the `data/metrics.yaml`
  line for each entry you looked up: delete it when you add a figure, otherwise add or
  re-date it. Commit metrics separately from new entries.
- **Review recognitions** → `awards.bib`: if the venue and year already has an `@award`, raise
  its `count`; otherwise add one with `title = {Special recognition for VENUE YYYY Papers
  (exceptional reviews)}` and `date = {YYYY}` (no count for a single one). Order within a year
  follows the file.
- **Reviewing / PC / editorial roles** → the matching list under SCHOLARLY AND PROFESSIONAL
  ACTIVITIES; extend an existing line's years rather than adding a duplicate line, and update
  its `\hlservice[years]`.
- **Grants** → a `@grant` entry in `grants.bib`; **students** → a `@supervision` entry in
  `supervision.bib` (see the comments at the top of each file). **Other awards** → an `@award` entry in
  `awards.bib`; for a paper or talk, also `icon = {award}` on that entry (see the top of
  `awards.bib`).
- Commit additions and corrections to existing entries separately.

## 5. Verify

Follow `.claude/skills/cv-verify/SKILL.md` (read it as a file if the skill isn't loaded).
Launch the verifiers in parallel in one message, giving them only the keys, the diff and
your change table — not your reasoning:
`citation-verifier`, `trainee-checker`, `apr-classifier`, `diff-auditor`, and
`chizen-figures` (with the changed files) when the diff touches `figures/` or `data/*.csv`, or adds a figure anywhere else.
If those agent types aren't available in your session, start general-purpose sub-agents
instead, each with the full text of the matching `.claude/agents/<name>.md` (below its
front matter) as its instructions, followed by the inputs.
If `latexmk` is available, compile `main.tex` and `apr.tex` and run
`python3 scripts/warning_ratchet.py main apr`; CI does both regardless. A warning your change
adds fails CI: fix it, or label the PR `needs-review` and ask. A warning your change fixes
(e.g. a DOI you backfilled) must leave `scripts/warnings-baseline.txt`:
`python3 scripts/check_cv.py --prune-baseline`, or delete the line CI names.

## 6. Label

`auto-merge` only when `scripts/check_cv.py` passes, every verifier that ran returns PASS, and every
change is one of:
- a new publication confirmed against a retrieved record (Crossref/DBLP/publisher page), or
  one the owner reported in an issue, marked `To appear`;
- a DOI backfill confirmed by `citation-verifier`;
- a review recognition, or a reviewing/PC/editorial role, stated in an official email or by the owner;
- an acceptance rate for the paper's own track, stated in its decision letter, the program
  chairs' email, the front matter or the venue's site; a journal impact factor (new or
  refreshed) stated on the publisher's or Clarivate's page; a `data/metrics.yaml` line.

A rate or impact factor from a third-party compilation or aggregator site, or from a track
you inferred, is `needs-review`.

Everything else is `needs-review`, with a **Questions for the owner** section of one-line yes/no
questions: corrections to existing entries, grants, supervision changes, awards other than
review recognitions, possible new trainees, anything unverifiable.

## 7. Open the PR (REST)

```
git push -u origin cv/weekly-YYYY-MM-DD
gh api repos/OWNER/REPO/pulls -f base=main \
  -f head=cv/weekly-YYYY-MM-DD -f title="CV update YYYY-MM-DD: <n> added, <m> updated" \
  -F body=@<body file>
gh api repos/OWNER/REPO/issues/<PR number>/labels -f 'labels[]=<label>'
```
(Create a missing label with `gh api repos/…/labels -f name=<label> -f color=<hex>`.)
Body: the change table (what / where / source), one line per verifier verdict, the questions,
and full verifier tables in a collapsed `<details>` block. Add "Closes #N" for each issue
handled, and comment the PR link on those issues.

Don't merge. The "CV auto-merge" workflow merges `auto-merge` PRs once CI passes.
If nothing needs changing, open no PR.

## 8. Final message (private to the owner)

Short: the PR link and its label (or "no changes"); items skipped and why, including private
ones such as conditional acceptances; questions; any source that was unavailable.

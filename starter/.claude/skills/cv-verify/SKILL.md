---
name: cv-verify
description: Verify CV changes with the deterministic checker and independent verifier sub-agents (four, plus `chizen-figures` when figures change), then decide the PR label. Use after any edit to scholar.bib or main.tex, or with "full" to audit every bib entry.
allowed-tools: Read, Grep, Glob, Edit, Agent, Bash(python3 scripts/check_cv.py:*), Bash(python3 scripts/warning_ratchet.py:*), Bash(git diff:*), Bash(git log:*), Bash(git status:*), Bash(git fetch:*), Bash(git show:*), Bash(curl:*)
---

# Verify CV changes

Arguments: none (verify the current branch against `origin/main`), or `full` (audit every entry).

## 1. Scope
- Normal: keys = bib keys added or changed in `git diff origin/main...HEAD -- scholar.bib`,
  plus keys whose `\addtocategory` membership changed in `main.tex`. Also note any other
  `main.tex` hunks (activities…) and any changed entries in `grants.bib`, `supervision.bib`,
  `awards.bib`, `service.bib` and `activities.bib`. Those come from the owner, not from a public record, so the citation verifier
  skips them; the checker validates their fields.
- `full`: every key in `scholar.bib`, in batches of about 15.

## 2. Deterministic checks first
Run `python3 scripts/check_cv.py`. Fix every **error** before going on (they mean the PDF is
wrong). Warnings on keys you touched: fix them if the fix is definite; otherwise carry them
into the PR as questions. Leave warnings on untouched keys alone.

## 3. Independent verifiers — in parallel, in one message
Launch these sub-agents together. Give each only the inputs listed (the key list, the diff,
the change table) and **not** your reasoning about why the change is right: they are useful
because they check from scratch.
- `citation-verifier` — keys (for `full`, one agent per batch, all batches in parallel)
- `trainee-checker` — keys
- `apr-classifier` — keys + diff (skip in `full` mode)
- `diff-auditor` — your draft change table (skip in `full` mode)
- `chizen-figures` — the changed figure files, when the diff touches `figures/` or `data/*.csv`, or adds a figure anywhere else. In `full` mode, give it `all`.

If those agent types aren't available in your session, start general-purpose sub-agents
instead, each given the full text of `.claude/agents/<name>.md` (below the front matter) as
its instructions, followed by its inputs. Tell `citation-verifier` that retrieved records are
on the `cv-sources` branch (`git fetch origin cv-sources`).

## 4. Act on the verdicts
- FIX rows that come with a retrieved source URL: apply exactly that fix, then re-run step 2
  and re-run only the verifier that raised it, on only those keys. At most two rounds.
- A FIX without a source, or verifiers disagreeing: don't apply it; it becomes a question.
- In `full` mode, corrections to existing entries go in one commit titled
  "Corrections from full audit" and the PR is always `needs-review`.

## 5. Decide the label
Use the rules in `automation/weekly-update.md`, section 6 ("Label"). In short: `auto-merge`
only when `check_cv.py` exits 0, every verifier's final VERDICT is PASS, and every change is of
a kind listed there; otherwise `needs-review`, with a **Questions for the owner** section listing each
open item as a one-line yes/no question.

## 6. Report
Put in the PR body: the change table (what / where / source), one line per verifier with its
verdict, and the questions. Paste full verifier tables in a collapsed `<details>` block.

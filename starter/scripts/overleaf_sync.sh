#!/usr/bin/env bash
# Keep the Overleaf project (via Overleaf's Git integration) in step with GitHub `main`.
#
# GitHub main is the source of truth. Each run does one of:
#   - Overleaf is behind main         -> fast-forward push main to Overleaf
#   - Overleaf has edits main lacks   -> merge them on branch overleaf-edits and open a PR
#                                        (labelled auto-merge, so CI checks and merges it)
#   - histories unrelated (first run) -> if the LaTeX content matches, open a one-time
#                                        PR on overleaf-link that joins the histories
# Tooling paths (workflows, scripts, Claude config) live only on GitHub; if Overleaf
# drops or changes them, the GitHub copies win.
#
# Env: OVERLEAF_TOKEN + OVERLEAF_PROJECT_ID (or OVERLEAF_URL for tests),
#      GH_TOKEN for gh, LINK_MODE=safe|github-wins (first run only), DRY_GH=1 to print gh calls.
set -euo pipefail

OL_URL="${OVERLEAF_URL:-https://git:${OVERLEAF_TOKEN:?}@git.overleaf.com/${OVERLEAF_PROJECT_ID:?}}"
MAIN_REF="${MAIN_REF:-origin/main}"
LINK_MODE="${LINK_MODE:-safe}"
PROTECTED=(.github .claude scripts data automation CLAUDE.md AUTOMATION.md .gitignore)
EXCLUDES=()
for p in "${PROTECTED[@]}"; do EXCLUDES+=(":(exclude)$p"); done

gh_() { if [ -n "${DRY_GH:-}" ]; then echo "[dry-run] gh $*"; else gh "$@"; fi; }
note() { echo "::notice::$*"; }

git config user.name  "overleaf-sync[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git remote remove overleaf >/dev/null 2>&1 || true
git remote add overleaf "$OL_URL"
git fetch --quiet overleaf

# Newer Overleaf projects use `main`, older ones `master`.
if git rev-parse -q --verify refs/remotes/overleaf/main >/dev/null; then OLB=main; else OLB=master; fi
OL="refs/remotes/overleaf/$OLB"

content_same() { git diff --quiet "$1" "$2" -- . "${EXCLUDES[@]}"; }

restore_protected() {
  for p in "${PROTECTED[@]}"; do
    if git cat-file -e "$MAIN_REF:$p" 2>/dev/null; then
      git rm -r -q --cached --ignore-unmatch -- "$p"
      git checkout "$MAIN_REF" -- "$p"
    else
      git rm -r -q --ignore-unmatch -- "$p"
    fi
  done
}

open_pr() { # branch title body label
  local existing
  existing=$(gh_ pr list --head "$1" --state open --json number --jq '.[0].number' 2>/dev/null || true)
  if [ -z "$existing" ] || [ -n "${DRY_GH:-}" ]; then
    gh_ label create "$4" --force >/dev/null 2>&1 || true
    gh_ pr create --base main --head "$1" --title "$2" --body "$3" --label "$4"
  fi
  # PRs and pushes made with the workflow token don't trigger other workflows; start CI explicitly.
  gh_ workflow run cv-build.yml --ref "$1"
}

if ! git merge-base "$MAIN_REF" "$OL" >/dev/null 2>&1; then
  # ---- first run: GitHub and Overleaf histories have never been joined
  if content_same "$MAIN_REF" "$OL" || [ "$LINK_MODE" = "github-wins" ]; then
    git checkout -q -B overleaf-link "$MAIN_REF"
    git merge -q -s ours --allow-unrelated-histories --no-edit \
      -m "Join Overleaf history (content from GitHub main)" "$OL"
    git push -q --force origin overleaf-link
    open_pr overleaf-link "Join Overleaf and GitHub histories" \
      "One-time merge so GitHub \`main\` can be pushed to Overleaf as a fast-forward. It changes no files. Merge with a merge commit (the auto-merge workflow does)." \
      auto-merge
    note "Opened the one-time history-joining PR; Overleaf will be updated after it merges."
    exit 0
  fi
  echo "::error::GitHub main and the Overleaf project have different LaTeX content and no shared history."
  echo "Bring them in line first (in Overleaf: Menu > GitHub > push your Overleaf changes, merge them on GitHub),"
  echo "or re-run this workflow with link_mode=github-wins to make Overleaf match GitHub (Overleaf keeps its old versions in History)."
  git diff --stat "$MAIN_REF" "$OL" -- . "${EXCLUDES[@]}" || true
  exit 1
fi

if git merge-base --is-ancestor "$OL" "$MAIN_REF"; then
  # ---- Overleaf is behind (or equal): fast-forward it
  if [ "$(git rev-parse "$OL")" != "$(git rev-parse "$MAIN_REF")" ]; then
    git push -q overleaf "$MAIN_REF:refs/heads/$OLB"
    note "Pushed main ($(git rev-parse --short "$MAIN_REF")) to Overleaf."
  else
    note "Overleaf already matches main."
  fi
  exit 0
fi

# ---- Overleaf has edits that main doesn't
git checkout -q -B overleaf-edits "$MAIN_REF"
if git merge -q --no-ff --no-commit "$OL" 2>/dev/null; then
  restore_protected
  # Commit even if nothing but tooling differed: the merge commit is what lets the
  # next run fast-forward Overleaf.
  git commit -q --no-edit -m "Merge edits from Overleaf"
  label=auto-merge
  body="Edits made in Overleaf since the last sync, merged onto \`main\`. Tooling files keep their GitHub versions. CI checks and compiles this, then merges it with a merge commit so Overleaf can be fast-forwarded."
else
  git merge --abort || true
  git checkout -q -B overleaf-edits "$OL"
  label=needs-review
  body="Overleaf edits conflict with \`main\`. Resolve on this branch (or comment \`@claude resolve the conflicts, keeping both sides' content\`), then merge with a merge commit."
fi
git push -q --force origin overleaf-edits
open_pr overleaf-edits "Edits from Overleaf" "$body" "$label"
note "Overleaf has new edits; opened/updated the overleaf-edits PR ($label)."

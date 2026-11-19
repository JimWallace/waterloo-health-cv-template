---
name: weekly-cv-update
description: Weekly unattended CV update - new publications and DOIs, open cv-item issues and Outlook notifications, verified by sub-agents, delivered as one labelled PR. The procedure lives in automation/weekly-update.md.
allowed-tools: Read, Grep, Glob, Edit, Write, Agent, WebFetch, WebSearch, Skill, Bash(python3 scripts/check_cv.py:*), Bash(python3 scripts/warning_ratchet.py:*), Bash(python3 scripts/fetch_candidates.py:*), Bash(git:*), Bash(gh api:*), Bash(curl:*), Bash(latexmk:*), Bash(date:*), Bash(jq:*)
---

Read `automation/weekly-update.md` in this repository and follow it exactly. It is kept as a
plain file so that any scheduled job, not only this skill, can run the same procedure.

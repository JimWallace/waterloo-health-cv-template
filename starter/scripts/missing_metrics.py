#!/usr/bin/env python3
"""List printed journal and conference papers whose note has no acceptance rate or
impact factor, and that data/metrics.yaml does not explain.

Reporting only: it never fails CI. Automated runs use it to find what to look up
(automation/weekly-update.md, step 2e).

    python3 scripts/missing_metrics.py               # missing, then unresolved
    python3 scripts/missing_metrics.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from cvlib import ROOT, parse_bib, parse_categories  # noqa: E402

METRIC = re.compile(r"Acceptance rate|Impact Factor", re.I)
CATEGORIES = ("journal", "conference")


def load_status(path):
    status = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, rest = line.split(":", 1)
        parts = [p.strip() for p in rest.split("|")]
        status[key.strip()] = {"status": parts[0], "reason": parts[1] if len(parts) > 1 else "",
                               "checked": parts[2] if len(parts) > 2 else ""}
    return status


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    bib = parse_bib(ROOT / "scholar.bib")
    entries = {e.key: e for e in bib.entries}
    cats = parse_categories(ROOT / "main.tex")
    status = load_status(ROOT / "data" / "metrics.yaml")

    missing, unresolved, stale = [], [], []
    for cat in CATEGORIES:
        for key in cats.get(cat, []):
            e = entries.get(key)
            if e is None:
                continue
            has = bool(METRIC.search(e.fields.get("note", "")))
            s = status.get(key)
            if has:
                if s:
                    stale.append({"key": key, "category": cat})
            elif s is None:
                missing.append({"key": key, "category": cat,
                                "year": e.fields.get("year", ""),
                                "venue": e.fields.get("booktitle") or e.fields.get("journal", "")})
            elif s["status"] == "unresolved":
                unresolved.append({"key": key, "category": cat, **s})
    unknown = [k for k in status if k not in entries]

    if args.json:
        print(json.dumps({"missing": missing, "unresolved": unresolved,
                          "stale": stale, "unknown": unknown}, indent=2))
        return
    print(f"## Missing ({len(missing)}): no figure in the note and not in data/metrics.yaml")
    for m in missing:
        print(f"- {m['key']} ({m['category']}, {m['year']}): {m['venue']}")
    print(f"\n## Unresolved ({len(unresolved)}): looked for before, worth retrying")
    for u in sorted(unresolved, key=lambda u: u["checked"]):
        print(f"- {u['key']}: {u['reason']} (last checked {u['checked']})")
    if stale:
        print("\n## Now in scholar.bib: delete these lines from data/metrics.yaml")
        for s in stale:
            print(f"- {s['key']}")
    if unknown:
        print("\n## In data/metrics.yaml but not in scholar.bib")
        for k in unknown:
            print(f"- {k}")


if __name__ == "__main__":
    main()

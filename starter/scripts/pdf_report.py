#!/usr/bin/env python3
"""Checks on the built PDFs, and what changed in them.

    python3 scripts/pdf_report.py main.pdf apr.pdf
    python3 scripts/pdf_report.py main.pdf apr.pdf --against ref/Quill-CV.pdf ref/Quill-CV-APR.pdf

Fails (exit 1) when a PDF has a font that is not embedded, or a Type 3
(bitmap) font: either one prints badly or is refused by a submission portal.
With --against (the PDFs on the cv-latest release, i.e. main), it also writes
the page counts and a diff of the PDF text to the report, and warns about any
heading that disappeared. Those are for the reviewer and never fail: the
text is what the CV says, so a dropped field or section shows up there even
when every check passes.

Needs poppler's pdfinfo, pdffonts and pdftotext.
"""
from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

MAX_DIFF_LINES = 400


def run(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def pages(pdf: Path) -> int:
    m = re.search(r"^Pages:\s+(\d+)", run("pdfinfo", str(pdf)), re.M)
    return int(m.group(1)) if m else 0


def font_problems(pdf: Path) -> list[str]:
    out = []
    lines = run("pdffonts", str(pdf)).splitlines()
    for ln in lines[2:]:
        # name type [encoding] emb sub uni object-id: the columns from the right are fixed
        cols = ln.split()
        if len(cols) < 7:
            continue
        emb, name = cols[-5], cols[0]
        ftype = " ".join(cols[1:-6])
        if emb != "yes":
            out.append(f"{pdf.name}: font {name} ({ftype}) is not embedded")
        if ftype.startswith("Type 3"):
            out.append(f"{pdf.name}: font {name} is a Type 3 (bitmap) font")
    return out


MONTHS = (r"(?:January|February|March|April|May|June|July|August|September|October"
          r"|November|December)")
FOOTER = re.compile(rf"{MONTHS} \d{{4}} #\d+|\d+|Page \d+( of \d+)?")
DATE = re.compile(rf"\b{MONTHS} \d{{1,2}}, \d{{4}}\b")
LABEL = re.compile(r"\[[A-Z]{1,3}\d+\]\s*")  # [J7], [C12]: renumber when an entry is added


def lines(pdf: Path) -> list[str]:
    raw = run("pdftotext", "-enc", "UTF-8", str(pdf), "-")
    out = [" ".join(ln.split()) for ln in raw.replace("\f", "\n").splitlines()]
    return [ln for ln in out if ln and not FOOTER.fullmatch(ln)]


def sentences(text_lines: list[str]) -> list[str]:
    """The text as sentences, so a diff does not depend on where lines or pages break."""
    flat = DATE.sub("<date>", " ".join(text_lines))
    flat = LABEL.sub("\n", flat)
    out = []
    for chunk in flat.split("\n"):
        out += [x.strip() for x in re.split(r"(?<=[a-z0-9)\]][.;:])\s+(?=[A-Z(\[])", chunk) if x.strip()]
    return out


def headings(text_lines: list[str]) -> set[str]:
    """Lines in capitals, and the APR notes: the CV's section headings."""
    return {ln for ln in text_lines if ln.startswith("A Note on ")
            or (len(ln) > 3 and ln.upper() == ln and re.search(r"[A-Z]{3}", ln))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+", type=Path)
    ap.add_argument("--against", nargs="+", type=Path, help="reference PDFs, in the same order")
    args = ap.parse_args()
    ref = args.against or []
    if ref and len(ref) != len(args.pdfs):
        ap.error("--against needs one reference PDF per PDF")

    report, problems, notices = ["## PDF checks", ""], [], []
    for i, pdf in enumerate(args.pdfs):
        problems += font_problems(pdf)
        n = pages(pdf)
        old = ref[i] if i < len(ref) and ref[i].exists() else None
        if not old:
            report.append(f"- `{pdf.name}`: {n} pages")
            continue
        report.append(f"- `{pdf.name}`: {n} pages (main: {pages(old)})")
        new_l, old_l = lines(pdf), lines(old)
        gone = sorted(headings(old_l) - headings(new_l))
        for h in gone:
            notices.append(f"{pdf.name}: heading '{h}' is no longer in the PDF")
        diff = list(difflib.unified_diff(sentences(old_l), sentences(new_l), f"main/{old.name}", f"this PR/{pdf.name}",
                                         n=1, lineterm=""))
        if diff:
            shown = diff[:MAX_DIFF_LINES]
            more = f"\n… {len(diff) - len(shown)} more lines" if len(diff) > len(shown) else ""
            report += ["", f"<details><summary>Text changes in {pdf.name} "
                       f"(+{sum(1 for d in diff if d[:1] == '+' and d[:3] != '+++')} "
                       f"−{sum(1 for d in diff if d[:1] == '-' and d[:3] != '---')} lines)</summary>",
                       "", "```diff", *shown, "```" + more, "</details>", ""]
        else:
            report.append("  - text unchanged from main")
    if problems:
        report += ["", "### Font problems", *[f"- {p}" for p in problems]]
    if notices:
        report += ["", "### Headings that disappeared", *[f"- {p}" for p in notices]]
    out = "\n".join(report) + "\n"
    print(out)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(out)
    if os.environ.get("GITHUB_ACTIONS"):
        for p in problems:
            print(f"::error title=PDF font::{p}")
        for p in notices:
            print(f"::warning title=Heading disappeared::{p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

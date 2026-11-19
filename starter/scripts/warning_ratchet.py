#!/usr/bin/env python3
"""The warning ratchet: a merge may not add a warning, and the list of accepted
warnings (scripts/warnings-baseline.txt) can only shrink.

Three sources feed it:
  check_cv   warnings from scripts/check_cv.py (check_cv.py applies the ratchet itself)
  <doc>.blg  biber's warnings for one document
  <doc>.log  LaTeX's warnings for one document (after latexmk's final pass)
where <doc> is main, apr, example or example-apr.

    python3 scripts/warning_ratchet.py main apr            # after latexmk main.tex / apr.tex
    python3 scripts/warning_ratchet.py example example-apr # after building template/example
    python3 scripts/warning_ratchet.py --prune main apr    # drop baseline lines that no longer occur
    python3 scripts/warning_ratchet.py --show main         # print the current warnings
    python3 scripts/warning_ratchet.py --growth origin/main  # fail if the baseline gained lines

Exit 1 when a warning is not in the baseline, when the baseline lists a warning
that no longer occurs (delete that line; --prune does it), or when the log has
an error. Every warning is an identifier without line numbers or sizes, so it
survives edits elsewhere in the file; a baseline line that occurs twice means
the warning occurs twice.

What counts in a LaTeX log, and why:
  - every "LaTeX/Package/Class ... Warning", "pdfTeX warning" and "Missing
    character" message, normalised (input line, page and pt values removed) and
    counted once per document, since some repeat on every page;
  - Overfull boxes wider than OVERFULL_PT, identified by the text TeX prints for
    the offending line (hyphenation points and fonts removed). Smaller overflows
    are invisible in print and vary with the TeX Live version;
  - not Underfull boxes: they mean loose spacing, not text in the margin, and
    the ones here come from forced line breaks and carry no text to identify
    them by. Their count is printed for information;
  - not "rerun" hints: latexmk reruns until the document is stable and fails if
    it cannot, so in the final log they are left over from an earlier pass.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "scripts" / "warnings-baseline.txt"
BASELINE_REL = "scripts/warnings-baseline.txt"
DOCS = {
    "main": ROOT / "main",
    "apr": ROOT / "apr",
    "example": ROOT / "template" / "example" / "example",
    "example-apr": ROOT / "template" / "example" / "example-apr",
}
OVERFULL_PT = 1.0
MAX_PRINT_LINE = 79  # TeX Live's default width of log lines

IGNORED = re.compile(
    r"Rerun to get|Label\(s\) may have changed|Please rerun LaTeX|Please \(re\)run Biber"
    r"|Package rerunfilecheck Warning|run Biber on the file|Temporary extra page added")

HEADER = """\
# Accepted warnings: the ratchet's baseline (see scripts/warning_ratchet.py).
# CI fails on any warning not listed here, and on any line here that no longer
# occurs, so this file only shrinks. Fix the cause rather than adding a line;
# a PR that adds lines cannot auto-merge (the owner merges it by hand).
# One line per occurrence: "<source>: <warning>".
"""


# ---------------------------------------------------------------- baseline

def read_baseline(text: str | None = None) -> Counter:
    if text is None:
        text = BASELINE.read_text(encoding="utf-8") if BASELINE.exists() else ""
    return Counter(ln.rstrip() for ln in text.splitlines()
                   if ln.strip() and not ln.lstrip().startswith("#"))


def write_baseline(lines: Counter) -> None:
    body = sorted(lines.elements(), key=lambda s: (s.split(":", 1)[0], s))
    BASELINE.write_text(HEADER + "".join(ln + "\n" for ln in body), encoding="utf-8")


def compare(current: Counter, baseline: Counter, sources: set[str]) -> tuple[list[str], list[str]]:
    """New warnings and stale baseline lines, restricted to `sources`."""
    base = Counter({k: n for k, n in baseline.items() if k.split(":", 1)[0] in sources})
    new = sorted((current - base).elements())
    stale = sorted((base - current).elements())
    return new, stale


# ---------------------------------------------------------------- check_cv

def check_cv_line(w: dict) -> str:
    msg = re.sub(r"\b[\w.-]+\.(?:bib|tex):\d+:\s*", "", w["msg"])
    return f"check_cv: {w['code']} {' '.join(msg.split())}"


# ---------------------------------------------------------------- biber

def biber_lines(blg: Path, source: str) -> tuple[list[str], list[str]]:
    """(warnings, errors) from a biber .blg file."""
    text = blg.read_text(encoding="utf-8", errors="replace")
    # biber copies each data source to a temp file named after the md5 of its name
    sources = {hashlib.md5(n.encode()).hexdigest(): n
               for n in re.findall(r"Found BibTeX data source '([^']+)'", text)}
    warns, errs = [], []
    for m in re.finditer(r"^\[\d+\] \S+> (WARN|ERROR) - (.*)$", text, re.M):
        level, msg = m.groups()
        msg = _biber_locate(msg, sources, blg.parent)
        (warns if level == "WARN" else errs).append(f"{source}: {msg}")
    return warns, errs


def _biber_locate(msg: str, sources: dict[str, str], where: Path) -> str:
    """Replace "<tempfile>, line N" by the .bib file and the entry at that line."""
    m = re.search(r"\S*/([0-9a-f]{32})_\d+\.utf8, line (\d+), (?:warning|error): ", msg)
    if not m:
        return msg
    name = sources.get(m.group(1), "a .bib file")
    line = int(m.group(2))
    entry = _entry_at(where / name, line) if name.endswith(".bib") else None
    rest = msg[m.end():]
    rest = re.sub(r"^\d+ characters of junk", "characters of junk", rest)
    place = f"{name}, at entry '{entry}'" if entry else name
    return f"{msg[:m.start()]}{place}: {rest}"


def _entry_at(bib: Path, line: int) -> str | None:
    """Key of the last entry that starts on or before `line` (biber reports junk
    at the line of the entry that follows it)."""
    if not bib.exists():
        return None
    key = None
    for i, ln in enumerate(bib.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if i > line:
            break
        m = re.match(r"\s*@\w+\s*[{(]\s*([^,\s]+)\s*,", ln)
        if m:
            key = m.group(1)
    return key


# ---------------------------------------------------------------- LaTeX log

def unwrap(raw: bytes) -> list[str]:
    """TeX breaks log lines at MAX_PRINT_LINE bytes; join them back up."""
    out: list[bytes] = []
    cont = False
    for ln in raw.split(b"\n"):
        ln = ln.rstrip(b"\r")
        if cont:
            out[-1] += ln
        else:
            out.append(ln)
        cont = len(ln) == MAX_PRINT_LINE
    return [x.decode("utf-8", errors="replace") for x in out]


def _norm_msg(s: str) -> str:
    s = re.sub(r"\s+on input line \d+\.?", "", s)
    s = re.sub(r"\s+on page \d+", "", s)
    s = re.sub(r"\(?-?\d+(?:\.\d+)?pt\)?", "#pt", s)
    return " ".join(s.split())


def _excerpt(lines: list[str], i: int) -> str:
    """The text TeX prints after a box warning, normalised to an identifier."""
    parts = []
    for ln in lines[i + 1:i + 8]:
        if not ln.strip():
            break
        parts.append(ln)
    s = " ".join(parts)
    s = re.sub(r"\\[A-Za-z0-9]+(?:/[^\s/]+)+ ?", "", s)  # font selectors like \OT1/ptm/m/n/12
    s = re.sub(r"\[\]|\$|-|\^\^[0-9a-f]{2}", "", s)        # rules, math shifts, hyphenation
    s = " ".join(s.split())
    return s[:60].rstrip() or "(no text)"


BOX = re.compile(r"^(Overfull|Underfull) \\([hv])box \((?:badness (\d+)|(-?[\d.]+)pt too (?:wide|high))\) (.*)$")
WARN = re.compile(r"^(?:(?:Package|Class|Module) (\S+)|LaTeX(?: Font)?) Warning: (.*)$")


def latex_lines(log: Path, source: str) -> tuple[list[str], list[str], Counter]:
    """(warnings, errors, ignored counts) from a LaTeX .log file."""
    lines = unwrap(log.read_bytes())
    warns: list[str] = []
    errs: list[str] = []
    ignored: Counter = Counter()
    seen: set[str] = set()

    def once(msg: str) -> None:
        if msg not in seen:
            seen.add(msg)
            warns.append(msg)

    for i, ln in enumerate(lines):
        if ln.startswith("! ") or re.match(r"^\.?/?[\w./-]+\.(?:tex|sty|cls|bbl|cfg|def):\d+: ", ln):
            errs.append(f"{source}: {ln.strip()}")
            continue
        m = BOX.match(ln)
        if m:
            kind, hv, _badness, size, where = m.groups()
            if kind == "Underfull":
                ignored["Underfull box"] += 1
            elif float(size) <= OVERFULL_PT:
                ignored[f"Overfull box of {OVERFULL_PT:g}pt or less"] += 1
            else:
                where = re.sub(r" at lines? [\d-]+| detected at line \d+", "", where)
                text = _excerpt(lines, i) if hv == "h" else ""
                warns.append(f"{source}: Overfull \\{hv}box {where}" + (f': "{text}"' if text else ""))
            continue
        m = WARN.match(ln)
        if m:
            body = [m.group(0)]
            for nxt in lines[i + 1:]:
                if re.match(r"^\([^)\s]+\)\s", nxt):
                    body.append(re.sub(r"^\([^)\s]+\)\s+", "", nxt))
                else:
                    break
            msg = " ".join(body)
            if IGNORED.search(msg):
                ignored["rerun hint"] += 1
            else:
                once(f"{source}: {_norm_msg(msg)}")
            continue
        if re.match(r"^pdfTeX warning", ln) or ln.startswith("Missing character: "):
            once(f"{source}: {_norm_msg(ln)}")
    return warns, errs, ignored


# ---------------------------------------------------------------- main

def collect(docs: list[str]) -> tuple[Counter, list[str], dict[str, Counter]]:
    current: Counter = Counter()
    errors: list[str] = []
    ignored: dict[str, Counter] = {}
    for d in docs:
        stem = DOCS[d]
        log, blg = stem.with_suffix(".log"), stem.with_suffix(".blg")
        if not log.exists():
            errors.append(f"{d}.log: not found ({log.relative_to(ROOT)}); did the document compile?")
            continue
        w, e, ig = latex_lines(log, f"{d}.log")
        current.update(w)
        errors += e
        ignored[f"{d}.log"] = ig
        if blg.exists():
            w, e = biber_lines(blg, f"{d}.blg")
            current.update(w)
            errors += e
        else:
            errors.append(f"{d}.blg: not found; biber did not run?")
    return current, errors, ignored


def report(title: str, new: list[str], stale: list[str], errors: list[str],
           notes: list[str], current: Counter) -> str:
    out = [f"## {title}", ""]
    if errors:
        out += ["### Errors", *[f"- `{e}`" for e in errors], ""]
    if new:
        out += ["### New warnings (not in the baseline)",
                "Fix the cause. Only if it cannot be fixed, add the line below to "
                f"`{BASELINE_REL}`; then the PR needs the owner to merge it by hand.", "```",
                *new, "```", ""]
    if stale:
        out += ["### Fixed warnings still in the baseline",
                f"Delete these lines from `{BASELINE_REL}` (or run "
                "`python3 scripts/warning_ratchet.py --prune <docs>`, or "
                "`python3 scripts/check_cv.py --prune-baseline`):", "```", *stale, "```", ""]
    if not (errors or new or stale):
        out += ["No errors, and no warnings beyond the baseline.", ""]
    out += notes
    out += ["<details><summary>All current warnings "
            f"({sum(current.values())})</summary>", "", "```",
            *sorted(current.elements()), "```", "</details>", ""]
    return "\n".join(out)


def annotate(new: list[str], stale: list[str], errors: list[str]) -> None:
    if not os.environ.get("GITHUB_ACTIONS"):
        return
    for e in errors:
        print(f"::error title=LaTeX error::{e}")
    for w in new:
        print(f"::error title=New warning::{w}")
    for s in stale:
        print(f"::error file={BASELINE_REL},title=Fixed warning still in the baseline::{s}")


def summary(text: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


def growth(base_ref: str) -> int:
    """Fail if the baseline has lines the base revision's baseline does not."""
    try:
        old = subprocess.run(["git", "show", f"{base_ref}:{BASELINE_REL}"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        print(f"{base_ref} has no {BASELINE_REL}; nothing to compare.")
        return 0
    added = sorted((read_baseline() - read_baseline(old)).elements())
    if not added:
        print(f"The baseline did not grow (compared with {base_ref}).")
        return 0
    text = "\n".join([
        "## Warning baseline grew",
        f"This PR accepts new warnings in `{BASELINE_REL}`, so it cannot merge automatically. "
        "Merge it by hand if they are acceptable.", "```", *added, "```"])
    print(text)
    summary(text)
    if os.environ.get("GITHUB_ACTIONS"):
        for a in added:
            print(f"::error file={BASELINE_REL},title=Baseline grew::{a}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("docs", nargs="*", metavar="DOC",
                    help=f"documents to check: {', '.join(DOCS)}")
    ap.add_argument("--prune", action="store_true", help="remove stale baseline lines for these docs")
    ap.add_argument("--update", action="store_true",
                    help="replace these docs' baseline lines with the current warnings "
                         "(for a TeX Live upgrade; the PR then needs a human merge)")
    ap.add_argument("--show", action="store_true", help="print the current warnings and exit")
    ap.add_argument("--growth", metavar="REF", help="fail if the baseline gained lines since REF")
    args = ap.parse_args()

    if args.growth:
        return growth(args.growth)
    if not args.docs:
        ap.error("name at least one document")
    for d in args.docs:
        if d not in DOCS:
            ap.error(f"unknown document '{d}' (choose from {', '.join(DOCS)})")

    current, errors, ignored = collect(args.docs)
    if args.show:
        print("\n".join(sorted(current.elements())))
        return 0
    sources = {f"{d}.{x}" for d in args.docs for x in ("log", "blg")}
    baseline = read_baseline()
    new, stale = compare(current, baseline, sources)

    if args.prune or args.update:
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        keep = baseline - Counter(stale)
        if args.update:
            keep = Counter({k: n for k, n in baseline.items()
                            if k.split(":", 1)[0] not in sources}) + current
        write_baseline(keep)
        print(f"Baseline: removed {len(stale)} line(s)" +
              (f", added {len(new)}" if args.update else "") + f" in {BASELINE_REL}.")
        return 0

    notes = [f"Not counted in {src}: " + ", ".join(f"{n} {k}" for k, n in sorted(ig.items()))
             for src, ig in ignored.items() if ig]
    notes = [*notes, ""] if notes else []
    text = report(f"Warning ratchet: {', '.join(args.docs)}", new, stale, errors, notes, current)
    print(text)
    summary(text)
    annotate(new, stale, errors)
    return 1 if (errors or new or stale) else 0


if __name__ == "__main__":
    sys.exit(main())

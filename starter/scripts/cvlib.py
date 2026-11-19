"""Shared helpers for the CV checks: a small BibTeX reader and a reader for
the category lists in main.tex. Standard library only, so CI needs no installs.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def config() -> dict:
    """Settings from cv.toml (owner, sources, template). Empty dict if absent."""
    path = ROOT / "cv.toml"
    if not path.exists():
        return {}
    import tomllib
    with path.open("rb") as f:
        return tomllib.load(f)


def config_value(dotted: str, default: str = "") -> str:
    node = config()
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return str(node)

# Categories that main.tex actually prints with \printcategory.
# (workshops and thesis exist but their \printcategory lines are commented out.)
PRINTED_CATEGORIES = [
    "journal", "conference", "technicalreports", "other",
    "patent", "software", "invited", "presentations",
]
# APR colour categories (see template/aprcv.sty). These do not print anything themselves.
APR_CATEGORIES = [
    "aprteaching", "aprservice", "apraward", "aprnone", "aprinclude",
    "apralsoteaching", "apralsoresearch", "apralsoservice", "apralsoaward",
]
KNOWN_TYPES = {
    "article", "inproceedings", "incollection", "inbook", "book", "misc",
    "techreport", "report", "thesis", "phdthesis", "mastersthesis", "patent",
    "software", "online", "unpublished", "proceedings", "collection",
    "manual", "booklet", "conference", "dataset",
}


@dataclass
class Entry:
    key: str
    type: str
    fields: dict[str, str]
    line: int
    raw: str

    @property
    def year(self) -> int | None:
        m = re.search(r"\d{4}", self.fields.get("year", "") or self.fields.get("date", ""))
        return int(m.group()) if m else None

    @property
    def authors(self) -> list[str]:
        a = self.fields.get("author", "")
        return [p.strip() for p in re.split(r"\s+and\s+", a) if p.strip()] if a else []


@dataclass
class Bib:
    entries: list[Entry] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def by_key(self) -> dict[str, list[Entry]]:
        out: dict[str, list[Entry]] = {}
        for e in self.entries:
            out.setdefault(e.key, []).append(e)
        return out


def _read_balanced(text: str, i: int, open_ch: str, close_ch: str) -> int:
    """Return the index just past the delimiter that closes text[i] (an opener)."""
    depth = 0
    j = i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return -1


def _parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    # Whole-line % comments inside an entry (e.g. "% pages = {--},") are
    # skipped by biber; without this the reader stopped at the first one and
    # missed every field after it.
    body = re.sub(r"(?m)^[ \t]*%.*$", "", body)
    i = 0
    n = len(body)
    while i < n:
        m = re.compile(r"\s*,?\s*([A-Za-z][\w:-]*)\s*=\s*").match(body, i)
        if not m:
            break
        name = m.group(1).lower()
        i = m.end()
        if i >= n:
            break
        if body[i] == "{":
            end = _read_balanced(body, i, "{", "}")
            if end < 0:
                break
            val = body[i + 1:end - 1]
            i = end
        elif body[i] == '"':
            j = i + 1
            depth = 0
            while j < n:
                if body[j] == "\\":
                    j += 2
                    continue
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                elif body[j] == '"' and depth == 0:
                    break
                j += 1
            val = body[i + 1:j]
            i = j + 1
        else:
            m2 = re.compile(r"[^,}\s]+").match(body, i)
            val = m2.group() if m2 else ""
            i = m2.end() if m2 else i + 1
        fields[name] = re.sub(r"\s+", " ", val).strip()
    return fields


def parse_bib(path: Path) -> Bib:
    text = path.read_text(encoding="utf-8")
    bib = Bib()
    for m in re.finditer(r"@(\w+)\s*([{(])", text):
        etype = m.group(1).lower()
        if etype in {"comment", "string", "preamble"}:
            continue
        start = m.end() - 1
        line = text.count("\n", 0, m.start()) + 1
        end = _read_balanced(text, start, m.group(2), "}" if m.group(2) == "{" else ")")
        if end < 0:
            bib.errors.append(f"{path.name}:{line}: entry @{m.group(1)} has unbalanced braces")
            continue
        inner = text[start + 1:end - 1]
        km = re.match(r"\s*([^,\s]+)\s*,", inner)
        if not km:
            bib.errors.append(f"{path.name}:{line}: entry @{m.group(1)} has no citation key")
            continue
        key = km.group(1)
        bib.entries.append(Entry(key, etype, _parse_fields(inner[km.end():]), line, text[m.start():end]))
    return bib


def strip_comments(tex: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in tex.splitlines())


def parse_categories(tex_path: Path) -> dict[str, list[str]]:
    """Map category name -> keys, in order, keeping duplicates (so they can be reported)."""
    tex = strip_comments(tex_path.read_text(encoding="utf-8"))
    cats: dict[str, list[str]] = {}
    for m in re.finditer(r"\\addtocategory\s*\{(\w+)\}\s*\{([^}]*)\}", tex):
        keys = [k.strip() for k in m.group(2).split(",") if k.strip()]
        cats.setdefault(m.group(1), []).extend(keys)
    return cats


def review_period(tex_path: Path) -> tuple[int, int] | None:
    tex = strip_comments(tex_path.read_text(encoding="utf-8"))
    m = re.search(r"\\setreviewperiod\{(\d{4})\}\{(\d{4})\}", tex)
    return (int(m.group(1)), int(m.group(2))) if m else None


# ---------------------------------------------------------------- names
def clean_name(raw: str) -> str:
    s = raw.replace("{\\dag}", "").replace("\\dag", "")
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = s.replace("*", "").replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def name_parts(raw: str) -> tuple[str, str]:
    """(family, given) for 'Family, Given' or 'Given Family'."""
    s = clean_name(raw)
    if "," in s:
        fam, giv = s.split(",", 1)
        return fam.strip(), giv.strip()
    bits = s.split()
    return (bits[-1], " ".join(bits[:-1])) if bits else ("", "")


def is_marked_trainee(raw: str) -> bool:
    return "*" in raw


def is_presenter(raw: str) -> bool:
    return "\\dag" in raw


def mark_in_given_name(raw: str) -> bool:
    """True for 'Family, G.*' style marks, which giveninits likely drops."""
    s = raw.replace("{\\dag}", "").replace("\\dag", "")
    if "," not in s or "*" not in s:
        return False
    fam, giv = s.split(",", 1)
    return "*" in giv and "*" not in fam


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def norm_title(t: str) -> str:
    t = re.sub(r"\\[a-zA-Z]+\s*", "", t)
    return norm(t)


def load_roster(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
        data = yaml.safe_load(text) or {}
        return data.get("trainees", []) or []
    except ImportError:
        return _read_roster_plain(text)


def _read_roster_plain(text: str) -> list[dict]:
    """Fallback for runners without PyYAML; handles the simple layout of trainees.yaml."""
    import json
    out: list[dict] = []
    for ln in text.splitlines():
        ln = re.sub(r"\s+#.*$", "", ln).rstrip()
        m = re.match(r"\s*-\s+name:\s*(.+)$", ln)
        if m:
            out.append({"name": m.group(1).strip().strip("'\"")})
            continue
        m = re.match(r"\s+(variants|level|from|to):\s*(.+)$", ln)
        if m and out:
            val = m.group(2).strip()
            out[-1][m.group(1)] = json.loads(val) if val.startswith("[") else val.strip("'\"")
    return out


def add_supervised(roster: list[dict], supervision: "Bib") -> tuple[list[dict], list[tuple[str, str, str]]]:
    """Everyone in supervision.bib is a trainee: add the students that the roster
    does not already name. Returns (roster, drift); drift lists (key, student,
    roster name) for a student whose family name is on the roster with a different
    given name: probably the same person spelled two ways, so a variant is missing."""
    idx = roster_index(roster)
    by_family: dict[str, list[str]] = {}
    for t in roster:
        for v in [t["name"]] + list(t.get("variants", []) or []):
            by_family.setdefault(norm(name_parts(v)[0]), []).append(t["name"])
    out, drift = list(roster), []
    for e in supervision.entries:
        author = e.fields.get("author", "")
        if not author:
            continue
        fam, giv = name_parts(author)
        if norm(fam + giv) in idx:
            continue
        near = sorted(set(by_family.get(norm(fam), [])))
        if near:
            drift.append((e.key, clean_name(f"{giv} {fam}"), near[0]))
            continue
        out.append({"name": clean_name(f"{giv} {fam}"), "variants": [author], "source": e.key})
    return out, drift


def roster_index(roster: list[dict]) -> dict[str, str]:
    """normalised variant -> canonical name"""
    idx: dict[str, str] = {}
    for t in roster:
        canon = t["name"]
        for v in [canon] + list(t.get("variants", []) or []):
            fam, giv = name_parts(v)
            idx[norm(fam + giv)] = canon
            idx[norm(clean_name(v))] = canon
    return idx


if __name__ == "__main__":
    # For workflows: python3 scripts/cvlib.py owner.pdf  -> prints the value ("" if unset)
    import sys
    print(config_value(sys.argv[1]) if len(sys.argv) > 1 else "")

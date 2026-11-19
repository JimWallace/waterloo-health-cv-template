#!/usr/bin/env python3
"""Collect publication records from public indexes and compare them with scholar.bib.

Writes .cv-work/candidates.json with three lists:
  new          works found in a source but not in scholar.bib (by DOI or title)
  doi_backfill entries in scholar.bib without a DOI that a source has a DOI for
  source_errors sources that could not be reached this run

With --records-dir it also saves the raw records Claude verifies against:
  <dir>/dblp-person.xml          DBLP's record of all the owner's publications
  <dir>/crossref/<doi>.json      Crossref metadata for every DOI in scholar.bib and in `new`
  <dir>/index.json               DOI -> bib key, and when each record was fetched
The "CV sources" workflow runs this on GitHub (which can reach these APIs) and
publishes the output on the cv-sources branch, so Claude sessions that can't reach
the APIs still verify against retrieved records. Standard library only.

Sources (cv.toml [sources], passed in by .github/workflows/cv-sources.yml; all optional):
  DBLP_PID            DBLP person id (computing venues)
  OPENALEX_AUTHOR_ID  OpenAlex author id, e.g. A5012345678 (health journals too);
                      if unset, resolved by owner.name + owner.affiliation in cv.toml
  ORCID               ORCID iD for a Crossref lookup
  CONTACT_EMAIL       sent as the polite-pool contact to OpenAlex and Crossref
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(__file__))
from cvlib import ROOT, config_value, norm_title, parse_bib  # noqa: E402

UA = "cv-weekly-update (waterloo-health-cv-template)"


def get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def clean_doi(d: str | None) -> str | None:
    if not d:
        return None
    d = d.strip().lower()
    for p in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if d.startswith(p):
            d = d[len(p):]
    return d or None


# ------------------------------------------------------------------ sources
def from_dblp(xml_bytes: bytes, since: int) -> list[dict]:
    out = []
    root = ET.fromstring(xml_bytes)
    for r in root.findall("r"):
        for rec in r:
            year = int(rec.findtext("year", "0") or 0)
            if year < since:
                continue
            doi = None
            urls = []
            for ee in rec.findall("ee"):
                u = (ee.text or "").strip()
                urls.append(u)
                if "doi.org/" in u:
                    doi = clean_doi(u)
            out.append({
                "source": "dblp",
                "source_id": rec.get("key"),
                "type": rec.tag,
                "title": "".join(rec.find("title").itertext()).rstrip(".") if rec.find("title") is not None else "",
                "authors": ["".join(a.itertext()) for a in rec.findall("author")],
                "venue": rec.findtext("booktitle") or rec.findtext("journal") or "",
                "year": year,
                "doi": doi,
                "urls": urls,
            })
    return out


def from_openalex(js: dict) -> list[dict]:
    out = []
    for w in js.get("results", []):
        loc = (w.get("primary_location") or {}).get("source") or {}
        out.append({
            "source": "openalex",
            "source_id": w.get("id"),
            "type": w.get("type"),
            "title": w.get("display_name") or "",
            "authors": [(a.get("author") or {}).get("display_name", "") for a in w.get("authorships", [])],
            "venue": loc.get("display_name") or "",
            "year": w.get("publication_year"),
            "doi": clean_doi(w.get("doi")),
            "urls": [x for x in [w.get("doi"), (w.get("primary_location") or {}).get("landing_page_url")] if x],
        })
    return out


def from_crossref(js: dict) -> list[dict]:
    out = []
    for it in (js.get("message") or {}).get("items", []):
        parts = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
        out.append({
            "source": "crossref",
            "source_id": it.get("DOI"),
            "type": it.get("type"),
            "title": (it.get("title") or [""])[0],
            "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])],
            "venue": (it.get("container-title") or [""])[0],
            "year": parts[0] if parts else None,
            "doi": clean_doi(it.get("DOI")),
            "urls": [it.get("URL")] if it.get("URL") else [],
        })
    return out


def crossref_record(doi: str, mailto: str) -> dict | None:
    q = f"?mailto={urllib.parse.quote(mailto)}" if mailto else ""
    js = json.loads(get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}{q}"))
    msg = js.get("message") or {}
    msg.pop("reference", None)  # long and not needed for checking an entry
    return msg


def safe_name(doi: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", doi)


def resolve_openalex_author(mailto: str) -> str | None:
    if not config_value("owner.name"):
        return None
    q = urllib.parse.urlencode({"search": config_value("owner.name"), "per-page": 25, **({"mailto": mailto} if mailto else {})})
    js = json.loads(get(f"https://api.openalex.org/authors?{q}"))
    for a in js.get("results", []):
        insts = a.get("last_known_institutions") or ([a["last_known_institution"]] if a.get("last_known_institution") else [])
        aff = config_value("owner.affiliation", "Waterloo").lower()
        if any(aff in (i or {}).get("display_name", "").lower() for i in insts):
            return a["id"].rsplit("/", 1)[-1]
    return None


# ------------------------------------------------------------------- compare
def compare(records: list[dict], bib_path) -> tuple[list[dict], list[dict]]:
    bib = parse_bib(bib_path)
    by_doi = {}
    by_title = {}
    for e in bib.entries:
        d = clean_doi(e.fields.get("doi"))
        if d:
            by_doi[d] = e.key
        t = norm_title(e.fields.get("title", ""))
        if t:
            by_title.setdefault(t, []).append(e)

    new: dict[str, dict] = {}
    backfill: dict[str, dict] = {}
    for r in records:
        t = norm_title(r["title"])
        if r["doi"] and r["doi"] in by_doi:
            continue
        if t and t in by_title:
            for e in by_title[t]:
                if "doi" not in e.fields and r["doi"]:
                    backfill.setdefault(e.key, {"key": e.key, "title": e.fields.get("title"), "candidates": []})
                    backfill[e.key]["candidates"].append(r)
            continue
        ident = r["doi"] or t
        if not ident:
            continue
        if ident in new:
            new[ident]["also_in"].append(r["source"])
        else:
            new[ident] = {**r, "also_in": []}
    return list(new.values()), list(backfill.values())


def save_crossref(out_dir: str, new: list[dict], backfill: list[dict], mailto: str,
                  errors: list[dict]) -> None:
    bib = parse_bib(ROOT / "scholar.bib")
    wanted: dict[str, list[str]] = {}
    for e in bib.entries:
        d = clean_doi(e.fields.get("doi"))
        if d:
            wanted.setdefault(d, []).append(e.key)
    for r in new:
        if r.get("doi"):
            wanted.setdefault(r["doi"], [])
    for b in backfill:
        for c in b["candidates"]:
            if c.get("doi"):
                wanted.setdefault(c["doi"], []).append(b["key"])
    os.makedirs(os.path.join(out_dir, "crossref"), exist_ok=True)
    index = {}
    for doi, keys in sorted(wanted.items()):
        entry = {"keys": keys, "file": None}
        try:
            rec = crossref_record(doi, mailto)
            fn = os.path.join("crossref", safe_name(doi) + ".json")
            with open(os.path.join(out_dir, fn), "w", encoding="utf-8") as fh:
                json.dump(rec, fh, indent=1, ensure_ascii=False)
            entry["file"] = fn
        except Exception as ex:  # noqa: BLE001  (a DOI that doesn't resolve is itself a finding)
            entry["error"] = repr(ex)
        index[doi] = entry
        time.sleep(0.2)
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as fh:
        json.dump({"fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                   "dois": index}, fh, indent=1)
    bad = [d for d, v in index.items() if v.get("error")]
    if bad:
        errors.append({"source": "crossref", "error": f"{len(bad)} DOI(s) not found: {', '.join(bad[:10])}"})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", type=int, default=dt.date.today().year - 1,
                    help="earliest publication year to consider (default: last year)")
    ap.add_argument("--out", default=str(ROOT / ".cv-work" / "candidates.json"))
    ap.add_argument("--dblp-xml", help="read DBLP XML from a file instead of the web (tests)")
    ap.add_argument("--openalex-json", help="read OpenAlex works JSON from a file (tests)")
    ap.add_argument("--records-dir", help="also save raw DBLP and Crossref records here")
    args = ap.parse_args()

    mailto = os.environ.get("CONTACT_EMAIL", "")
    records: list[dict] = []
    errors: list[dict] = []
    resolved = {}

    # DBLP
    try:
        if args.dblp_xml:
            xml_bytes = open(args.dblp_xml, "rb").read()
        else:
            pid = os.environ.get("DBLP_PID") or config_value("sources.dblp_pid")
            xml_bytes = get(f"https://dblp.org/pid/{pid}.xml") if pid else b""
        if xml_bytes:
            records += from_dblp(xml_bytes, args.since)
            if args.records_dir:
                os.makedirs(args.records_dir, exist_ok=True)
                with open(os.path.join(args.records_dir, "dblp-person.xml"), "wb") as fh:
                    fh.write(xml_bytes)
    except Exception as ex:  # noqa: BLE001
        errors.append({"source": "dblp", "error": repr(ex)})

    # OpenAlex
    try:
        if args.openalex_json:
            records += from_openalex(json.load(open(args.openalex_json)))
        elif not args.dblp_xml:
            aid = (os.environ.get("OPENALEX_AUTHOR_ID") or config_value("sources.openalex_author_id")
                   or resolve_openalex_author(mailto))
            resolved["openalex_author_id"] = aid
            if aid:
                q = urllib.parse.urlencode({
                    "filter": f"author.id:{aid},from_publication_date:{args.since}-01-01",
                    "per-page": 200, **({"mailto": mailto} if mailto else {})})
                records += from_openalex(json.loads(get(f"https://api.openalex.org/works?{q}")))
    except Exception as ex:  # noqa: BLE001
        errors.append({"source": "openalex", "error": repr(ex)})

    # Crossref by ORCID
    orcid = os.environ.get("ORCID") or config_value("sources.orcid")
    if orcid and not args.dblp_xml:
        try:
            q = urllib.parse.urlencode({"filter": f"orcid:{orcid},from-pub-date:{args.since}",
                                        "rows": 200, **({"mailto": mailto} if mailto else {})})
            records += from_crossref(json.loads(get(f"https://api.crossref.org/works?{q}")))
        except Exception as ex:  # noqa: BLE001
            errors.append({"source": "crossref", "error": repr(ex)})

    new, backfill = compare(records, ROOT / "scholar.bib")

    if args.records_dir and not args.dblp_xml:
        save_crossref(args.records_dir, new, backfill, mailto, errors)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    result = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "since": args.since,
        "resolved": resolved,
        "records_seen": len(records),
        "new": new,
        "doi_backfill": backfill,
        "source_errors": errors,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print(f"{len(records)} records; {len(new)} not in scholar.bib; "
          f"{len(backfill)} DOI backfills; {len(errors)} source error(s) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

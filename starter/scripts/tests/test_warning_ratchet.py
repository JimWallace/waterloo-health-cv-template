"""Tests for the warning ratchet's parsers.   python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import warning_ratchet as wr  # noqa: E402


def log_file(text: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "doc.log"
    p.write_bytes(text.encode("utf-8"))
    return p


class LatexLog(unittest.TestCase):
    def parse(self, text: str):
        return wr.latex_lines(log_file(text), "main.log")

    def test_unwrap_joins_lines_at_the_log_width(self):
        first = "x" * 79
        self.assertEqual(wr.unwrap(f"{first}\nyz\nnext\n".encode()), [first + "yz", "next", ""])

    def test_overfull_box_is_named_by_its_text_without_hyphens_fonts_or_numbers(self):
        a, _, _ = self.parse("Overfull \\hbox (13.40332pt too wide) in paragraph at lines 269--269\n"
                             "\\OT1/ptm/m/n/12 serendip-i-tous group in-ter-ac-tion\n []\n\n")
        b, _, _ = self.parse("Overfull \\hbox (14.1pt too wide) in paragraph at lines 301--302\n"
                             "\\T1/ptm/m/n/12 serendipi-tous group inter-ac-tion\n []\n\n")
        self.assertEqual(a, ['main.log: Overfull \\hbox in paragraph: "serendipitous group interaction"'])
        self.assertEqual(a, b)

    def test_small_overfull_and_underfull_boxes_are_not_counted(self):
        w, _, ig = self.parse("Overfull \\hbox (0.5pt too wide) in paragraph at lines 1--1\nab\n\n"
                              "Underfull \\hbox (badness 10000) in paragraph at lines 2--3\n\n []\n\n")
        self.assertEqual(w, [])
        self.assertEqual(ig["Underfull box"], 1)

    def test_identical_boxes_count_twice_messages_once(self):
        box = "Overfull \\hbox (55.7pt too wide) in alignment at lines 326--326\n [] [] []\n []\n\n"
        msg = "Package fancyhdr Warning: \\headheight is too small (12.0pt): \n"
        w, _, _ = self.parse(box + box + msg + msg)
        self.assertEqual(Counter(w), Counter({'main.log: Overfull \\hbox in alignment: "(no text)"': 2,
                                              "main.log: Package fancyhdr Warning: \\headheight is too small #pt:": 1}))

    def test_package_warning_continuation_and_input_line_are_normalised(self):
        w, _, _ = self.parse("Package foo Warning: Something odd\n(foo)                on input line 12.\n\n")
        self.assertEqual(w, ["main.log: Package foo Warning: Something odd"])

    def test_citation_keys_keep_their_digits(self):
        w, _, _ = self.parse("LaTeX Warning: Citation `wong2026ipv' on page 3 undefined on input line 45.\n")
        self.assertEqual(w, ["main.log: LaTeX Warning: Citation `wong2026ipv' undefined"])

    def test_rerun_hints_are_ignored_and_errors_reported(self):
        w, e, _ = self.parse("LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.\n"
                             "Package biblatex Warning: Please (re)run Biber on the file:\n(biblatex) main\n"
                             "./main.tex:12: Undefined control sequence.\n! Emergency stop.\n")
        self.assertEqual(w, [])
        self.assertEqual(len(e), 2)


class Biber(unittest.TestCase):
    def test_junk_warning_names_the_bib_file_and_entry_not_the_line(self):
        d = Path(tempfile.mkdtemp())
        (d / "scholar.bib").write_text("@article{a2020x,\n}\n\nstray = {x},\n@article{b2021y,\n}\n")
        h = hashlib.md5(b"scholar.bib").hexdigest()
        (d / "main.blg").write_text(
            "[368] bibtex.pm:1519> INFO - Found BibTeX data source 'scholar.bib'\n"
            f"[4218] Biber.pm:131> WARN - BibTeX subsystem: /tmp/biber_tmp_W/{h}_6553.utf8, line 5, "
            "warning: 12 characters of junk seen at toplevel\n"
            "[4218] Biber.pm:131> WARN - legacy month field 'Mar' in entry 'm2018s' is not an integer\n"
            "[4219] Biber.pm:131> ERROR - something broke\n")
        w, e = wr.biber_lines(d / "main.blg", "main.blg")
        self.assertEqual(w, ["main.blg: BibTeX subsystem: scholar.bib, at entry 'b2021y': "
                             "characters of junk seen at toplevel",
                             "main.blg: legacy month field 'Mar' in entry 'm2018s' is not an integer"])
        self.assertEqual(e, ["main.blg: something broke"])


class Ratchet(unittest.TestCase):
    def test_new_and_stale_are_per_source_and_count_duplicates(self):
        base = Counter({"main.log: A": 2, "main.log: B": 1, "apr.log: C": 1, "check_cv: D": 1})
        cur = Counter({"main.log: A": 1, "main.log: E": 1})
        new, stale = wr.compare(cur, base, {"main.log", "main.blg"})
        self.assertEqual(new, ["main.log: E"])
        self.assertEqual(stale, ["main.log: A", "main.log: B"])

    def test_baseline_ignores_comments_and_blank_lines(self):
        self.assertEqual(wr.read_baseline("# c\n\nx: 1\nx: 1\n"), Counter({"x: 1": 2}))

    def test_check_cv_lines_drop_file_line_numbers(self):
        self.assertEqual(wr.check_cv_line({"code": "W-record", "msg": "grants.bib:12: grant 'g' has role 'X'"}),
                         "check_cv: W-record grant 'g' has role 'X'")


if __name__ == "__main__":
    unittest.main()

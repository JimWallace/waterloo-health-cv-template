"""Tests for check_cv.py's exemptions.   python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_cv  # noqa: E402
import cvlib  # noqa: E402

MAIN_TEX = r"""
\DeclareBibliographyCategory{conference}
\addtocategory{conference}{plain2020, exempt2020, emptyreason2020, both2020}
\DeclareBibliographyCategory{unprinted}
\addtocategory{unprinted}{kept2020, both2020}
"""

SCHOLAR_BIB = r"""
@inproceedings{plain2020, title = {A}, year = {2020}}
@inproceedings{exempt2020, title = {B}, year = {2020}, nodoi = {Poster; no proceedings}}
@inproceedings{emptyreason2020, title = {C}, year = {2020}, nodoi = {}}
@inproceedings{both2020, title = {D}, year = {2020}, doi = {10.1/x}}
@misc{kept2020, title = {E}, year = {2020}}
@misc{stray2020, title = {F}, year = {2020}}
"""


class FieldReader(unittest.TestCase):
    def test_fields_after_a_commented_line_are_read(self):
        d = Path(tempfile.mkdtemp())
        p = d / "x.bib"
        p.write_text("@inproceedings{k,\n  year = {2026},\n  % pages = {--},\n  doi = {10.1/y},\n}\n",
                     encoding="utf-8")
        self.assertEqual(cvlib.parse_bib(p).entries[0].fields.get("doi"), "10.1/y")


class Exemptions(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "data").mkdir()
        shutil.copy(cvlib.ROOT / "data" / "trainees.yaml", self.root / "data" / "trainees.yaml")
        for name in check_cv.RECORD_FILES:
            (self.root / name).write_text("", encoding="utf-8")
        (self.root / "main.tex").write_text(MAIN_TEX, encoding="utf-8")
        (self.root / "scholar.bib").write_text(SCHOLAR_BIB, encoding="utf-8")
        self.saved = check_cv.ROOT
        check_cv.ROOT = self.root

    def tearDown(self):
        check_cv.ROOT = self.saved
        shutil.rmtree(self.root)

    def warnings(self, code):
        return {(w["key"], w["msg"]) for w in check_cv.run()["warnings"] if w["code"] == code}

    def test_nodoi_with_a_reason_silences_the_missing_doi_warning(self):
        keys = {k for k, _ in self.warnings("W-nodoi")}
        self.assertIn("plain2020", keys)
        self.assertNotIn("exempt2020", keys)

    def test_empty_nodoi_still_warns(self):
        msgs = [m for k, m in self.warnings("W-nodoi") if k == "emptyreason2020"]
        self.assertEqual(len(msgs), 1)
        self.assertIn("empty nodoi", msgs[0])

    def test_unprinted_category_silences_the_unprinted_warning(self):
        keys = {k for k, _ in self.warnings("W-unprinted")}
        self.assertIn("stray2020", keys)
        self.assertNotIn("kept2020", keys)
        self.assertFalse(self.warnings("W-cat"))

    def test_a_key_both_printed_and_unprinted_warns(self):
        msgs = [m for k, m in self.warnings("W-unprinted") if k == "both2020"]
        self.assertEqual(len(msgs), 1)
        self.assertIn("also in conference", msgs[0])



class ServiceRecords(unittest.TestCase):
    """service.bib: each role needs a title, a level some \\printservice prints, and YYYY[/YYYY]."""

    def errors(self, service_bib):
        records = {name: cvlib.parse_bib(self.write(name, "")) for name in check_cv.RECORD_FILES}
        records["service.bib"] = cvlib.parse_bib(self.write("service.bib", service_bib))
        found = []
        check_cv.check_records(records, "\\printservice{school}\n% \\printservice{faculty}\n",
                               lambda code, msg, key=None: found.append((key, msg)),
                               lambda *a, **k: None)
        return found

    def write(self, name, text):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_a_well_formed_role_passes(self):
        self.assertEqual(self.errors("@service{ok, title = {A Committee}, level = {school}, "
                                     "date = {2023/2025}, years = {2023, 2025}}\n"), [])

    def test_an_unprinted_level_is_an_error(self):
        # faculty is only in a comment, so nothing prints it
        errs = self.errors("@service{lost, title = {A Committee}, level = {faculty}, date = {2023}}\n")
        self.assertEqual([k for k, _ in errs], ["lost"])
        self.assertIn("no \\printservice", errs[0][1])

    def test_an_ongoing_role_and_several_levels_pass(self):
        self.assertEqual(self.errors("@service{ongoing, title = {A Committee}, level = {school}, date = {2021/}}\n"
                                     "@service{both, title = {A Chair}, level = {school, school}, date = {2024}}\n"), [])

    def test_each_named_level_must_be_printed(self):
        # school is printed, faculty is only in a comment
        errs = self.errors("@service{half, title = {A Chair}, level = {school, faculty}, date = {2024}}\n")
        self.assertEqual([k for k, _ in errs], ["half"])
        self.assertIn("'faculty'", errs[0][1])

    def test_a_bad_date_is_an_error(self):
        errs = self.errors("@service{when, title = {A Committee}, level = {school}, date = {2023 -- 2025}}\n")
        self.assertEqual([k for k, _ in errs], ["when"])
        self.assertIn("YYYY/YYYY", errs[0][1])


class CommitteeRecords(unittest.TestCase):
    """committees.bib: author or count, a counted degree, a date the template reads."""

    MAIN = "\\cvcommitteegroup{MSc}{MSc, MASc}\n\\printcommitteecounts{MSc, PhD}\n"

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def errors(self, committees_bib):
        records = {name: cvlib.parse_bib(self.write(name, "")) for name in check_cv.RECORD_FILES}
        records["committees.bib"] = cvlib.parse_bib(self.write("committees.bib", committees_bib))
        found = []
        check_cv.check_records(records, self.MAIN, lambda code, msg, key=None: found.append((key, msg)),
                               lambda *a, **k: None)
        return found

    def write(self, name, text):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_named_ongoing_and_count_only_records_pass(self):
        self.assertEqual(self.errors(
            "@committee{a, author = {Student, A.}, degree = {MASc}, date = {2024/}}\n"
            "@committee{b, author = {Student, B.}, degree = {PhD}, date = {2023/2025}}\n"
            "@committee{c, degree = {PhD}, date = {2019}, count = {4}}\n"), [])

    def test_a_degree_nothing_counts_is_an_error(self):
        errs = self.errors("@committee{a, author = {Student, A.}, degree = {MMath}, date = {2024}}\n")
        self.assertEqual([k for k, _ in errs], ["a"])
        self.assertIn("cvcommitteegroup", errs[0][1])

    def test_author_and_count_together_is_an_error(self):
        errs = self.errors("@committee{a, author = {Student, A.}, degree = {PhD}, date = {2024}, count = {2}}\n")
        self.assertIn("exactly one of author", errs[0][1])

    def test_a_count_over_a_range_is_an_error(self):
        errs = self.errors("@committee{a, degree = {PhD}, date = {2019/2020}, count = {2}}\n")
        self.assertEqual([k for k, _ in errs], ["a"])


class CourseRecords(unittest.TestCase):
    """courses.bib: course, title, a term-start date, digits for enrolment, Item=score pairs."""

    def errors(self, courses_bib):
        records = {name: cvlib.parse_bib(self.write(name, "")) for name in check_cv.RECORD_FILES}
        records["courses.bib"] = cvlib.parse_bib(self.write("courses.bib", courses_bib))
        found = []
        check_cv.check_records(records, "", lambda code, msg, key=None: found.append((key, msg)),
                               lambda *a, **k: None)
        return found

    def write(self, name, text):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_a_well_formed_course_passes(self):
        self.assertEqual(self.errors("@course{ok, course = {HLTH 101}, title = {A Course}, date = {2024-09}, "
                                     "enrolment = {40}, scp = {Implementation=4.5, Design=4.0}, "
                                     "scpaverage = {Course Overall=4.1}}\n"), [])

    def test_a_date_that_is_not_a_term_start_is_an_error(self):
        errs = self.errors("@course{when, course = {HLTH 101}, title = {A Course}, date = {2024-10}}\n")
        self.assertEqual([k for k, _ in errs], ["when"])
        self.assertIn("Fall", errs[0][1])

    def test_malformed_scores_are_an_error(self):
        errs = self.errors("@course{bad, course = {HLTH 101}, title = {A Course}, date = {2024-01}, "
                           "scp = {Implementation = 4.5/5}, enrolment = {~40}}\n")
        self.assertEqual(len(errs), 2)
        self.assertTrue(any("enrolment" in m for _, m in errs))
        self.assertTrue(any("scp 'Implementation = 4.5/5'" in m for _, m in errs))


if __name__ == "__main__":
    unittest.main()


class SupervisedTrainees(unittest.TestCase):
    """supervision.bib students count as trainees; a respelled one is flagged."""

    ROSTER = [
        {"name": "Liudmila Tahai", "variants": ["Tahai, Liudmila"]},
        {"name": "Robert P. Gauthier", "variants": ["Robert Gauthier"]},
    ]

    def supervision(self, *authors):
        d = Path(tempfile.mkdtemp())
        p = d / "supervision.bib"
        p.write_text("".join(f"@supervision{{s{i}, author = {{{a}}}, degree = {{PhD}}, status = {{In progress}}}}\n"
                             for i, a in enumerate(authors)), encoding="utf-8")
        return cvlib.parse_bib(p)

    def test_a_new_student_joins_the_roster(self):
        roster, drift = cvlib.add_supervised(self.ROSTER, self.supervision("Liaqat, Taha"))
        self.assertEqual(drift, [])
        self.assertIn("taha", {cvlib.norm(n) for n in [cvlib.name_parts(t["name"])[1] for t in roster]})
        self.assertIn(cvlib.norm("liaqattaha"), cvlib.roster_index(roster))

    def test_a_student_already_named_is_not_added_twice(self):
        roster, drift = cvlib.add_supervised(self.ROSTER, self.supervision("Gauthier, Robert"))
        self.assertEqual((len(roster), drift), (2, []))

    def test_a_respelled_student_is_flagged(self):
        _, drift = cvlib.add_supervised(self.ROSTER, self.supervision("Tahai, Mila"))
        self.assertEqual(drift, [("s0", "Mila Tahai", "Liudmila Tahai")])

    def test_the_real_files_are_consistent(self):
        roster = cvlib.load_roster(cvlib.ROOT / "data" / "trainees.yaml")
        _, drift = cvlib.add_supervised(roster, cvlib.parse_bib(cvlib.ROOT / "supervision.bib"))
        self.assertEqual(drift, [])

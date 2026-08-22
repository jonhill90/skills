from __future__ import annotations

import datetime
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "eval_status.py"
SPEC = importlib.util.spec_from_file_location("eval_status", SCRIPT_PATH)
assert SPEC and SPEC.loader
eval_status = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = eval_status
SPEC.loader.exec_module(eval_status)


def unevaluated(name: str) -> dict:
    return {"verdict": "unevaluated", "date": None, "evidence": None}


def evaluated(verdict: str, date: str = "2026-08-22", evidence: str = "README.md") -> dict:
    # README.md always exists in this repo -- a real, checkable evidence
    # path any test can use without writing its own fixture file for it.
    return {"verdict": verdict, "date": date, "evidence": evidence}


class TestCheck(unittest.TestCase):
    def test_clean_record_has_no_findings(self):
        record = {"a": unevaluated("a"), "b": evaluated("keep")}
        findings = eval_status.check(record, {"a", "b"})
        self.assertEqual(findings, [])

    def test_skill_dir_with_no_entry_is_a_finding(self):
        record = {"a": unevaluated("a")}
        findings = eval_status.check(record, {"a", "b"})
        self.assertTrue(any("b" in f and "no entry" in f for f in findings))

    def test_entry_with_no_skill_dir_is_stale(self):
        record = {"a": unevaluated("a"), "ghost": unevaluated("ghost")}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("ghost" in f and "stale" in f for f in findings))

    def test_unknown_verdict_is_a_finding(self):
        record = {"a": {"verdict": "maybe", "date": None, "evidence": None}}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("maybe" in f for f in findings))

    def test_unevaluated_with_date_set_is_a_finding(self):
        """unevaluated must mean NO eval ran -- date/evidence set alongside
        it is a contradiction, not a richer record."""
        record = {"a": {"verdict": "unevaluated", "date": "2026-08-22", "evidence": None}}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("unevaluated but date/evidence is set" in f for f in findings))

    def test_evaluated_verdict_missing_date_is_a_finding(self):
        record = {"a": {"verdict": "keep", "date": None, "evidence": "README.md"}}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("date is not set" in f for f in findings))

    def test_evaluated_verdict_missing_evidence_is_a_finding(self):
        record = {"a": {"verdict": "keep", "date": "2026-08-22", "evidence": None}}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("evidence is not set" in f for f in findings))

    def test_evidence_path_that_does_not_exist_is_a_finding(self):
        record = {"a": evaluated("keep", evidence="skills/nonexistent/references/eval-result.md")}
        findings = eval_status.check(record, {"a"})
        self.assertTrue(any("does not exist in this repo" in f for f in findings))

    def test_could_not_measure_is_a_valid_verdict_not_unevaluated(self):
        """could_not_measure means an eval ran and produced no reliable
        signal -- a different, real state from unevaluated (no eval ran at
        all). Both must be representable and neither should collapse into
        the other."""
        record = {"a": evaluated("could_not_measure")}
        findings = eval_status.check(record, {"a"})
        self.assertEqual(findings, [])


class TestLoadRecordAndDiscovery(unittest.TestCase):
    def test_load_record_missing_file_raises(self):
        with self.assertRaises(eval_status.RecordError):
            eval_status.load_record(Path("/nonexistent/eval-status.json"))

    def test_load_record_malformed_json_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("not json", encoding="utf-8")
            with self.assertRaises(eval_status.RecordError):
                eval_status.load_record(path)

    def test_load_record_missing_skills_key_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"nope": {}}), encoding="utf-8")
            with self.assertRaises(eval_status.RecordError):
                eval_status.load_record(path)

    def test_discover_skill_names_missing_dir_raises(self):
        with self.assertRaises(eval_status.RecordError):
            eval_status.discover_skill_names(Path("/nonexistent/skills"))

    def test_discover_skill_names_finds_directories_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real-skill").mkdir()
            (root / "not-a-skill.txt").write_text("x", encoding="utf-8")
            names = eval_status.discover_skill_names(root)
            self.assertEqual(names, {"real-skill"})


class TestMainCLI(unittest.TestCase):
    def test_unevaluated_flag_lists_only_unevaluated_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "a").mkdir(parents=True)
            (root / "skills" / "z").mkdir(parents=True)
            (root / "docs").mkdir()
            record_path = root / "docs" / "eval-status.json"
            record_path.write_text(json.dumps({"skills": {
                "a": {"verdict": "unevaluated", "date": None, "evidence": None},
                "z": {"verdict": "keep", "date": "2026-08-22", "evidence": None},
            }}), encoding="utf-8")

            orig_record, orig_root = eval_status.RECORD_PATH, eval_status.SKILLS_ROOT
            eval_status.RECORD_PATH = record_path
            eval_status.SKILLS_ROOT = root / "skills"
            try:
                import io
                from contextlib import redirect_stdout
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = eval_status.main(["--unevaluated"])
                self.assertEqual(rc, 0)
                self.assertEqual(buf.getvalue().splitlines(), ["a"])
            finally:
                eval_status.RECORD_PATH, eval_status.SKILLS_ROOT = orig_record, orig_root

    def test_real_record_is_clean(self):
        """The actual docs/eval-status.json this repo ships must pass its
        own check -- the property this script exists to guarantee, checked
        against the real file, not only a synthetic fixture."""
        rc = eval_status.main([])
        self.assertEqual(rc, 0)


class TestDumpRecord(unittest.TestCase):
    def test_dump_record_is_a_noop_round_trip_on_the_real_file(self):
        """--record's whole safety case rests on dump_record reproducing
        this file's existing one-line-per-skill shape exactly -- a
        formatter that reindented the whole file on every write would
        turn a one-skill change into an unreviewable whole-file diff.
        Checked against the REAL shipped file, not a synthetic one."""
        doc = eval_status.load_full_doc(eval_status.RECORD_PATH)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "roundtrip.json"
            eval_status.dump_record(doc, out)
            self.assertEqual(out.read_text(encoding="utf-8"),
                              eval_status.RECORD_PATH.read_text(encoding="utf-8"))

    def test_dump_record_sorts_and_updates_one_entry(self):
        doc = {"$comment": "c", "skills": {
            "z": {"verdict": "unevaluated", "date": None, "evidence": None},
            "a": {"verdict": "keep", "date": "2026-01-01", "evidence": "README.md"},
        }}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "r.json"
            eval_status.dump_record(doc, out)
            text = out.read_text(encoding="utf-8")
            # "a" sorts before "z"
            self.assertLess(text.index('"a":'), text.index('"z":'))
            reloaded = eval_status.load_full_doc(out)
            self.assertEqual(reloaded, doc)


class TestRecordCLI(unittest.TestCase):
    """--record is the one supported write path for docs/eval-status.json
    (estate-loop/agent-b2.md's own rule: "never by hand") -- these tests
    run against a throwaway copy of the record and skills tree, never the
    real shipped file, restoring eval_status's module globals afterward."""

    def _sandbox(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "skills" / "a-skill" / "references").mkdir(parents=True)
        (tmp / "skills" / "a-skill" / "references" / "eval-result.md").write_text(
            "evidence\n", encoding="utf-8")
        (tmp / "docs").mkdir()
        (tmp / "docs" / "eval-status.json").write_text(json.dumps({
            "$comment": "c",
            "skills": {"a-skill": {"verdict": "unevaluated", "date": None, "evidence": None}},
        }), encoding="utf-8")
        return tmp

    def setUp(self):
        self.orig_repo = eval_status.REPO
        self.orig_record = eval_status.RECORD_PATH
        self.orig_skills = eval_status.SKILLS_ROOT
        self.tmp = self._sandbox()
        eval_status.REPO = self.tmp
        eval_status.RECORD_PATH = self.tmp / "docs" / "eval-status.json"
        eval_status.SKILLS_ROOT = self.tmp / "skills"

    def tearDown(self):
        eval_status.REPO = self.orig_repo
        eval_status.RECORD_PATH = self.orig_record
        eval_status.SKILLS_ROOT = self.orig_skills
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_record_writes_a_valid_entry(self):
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22",
        ])
        self.assertEqual(rc, 0)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"], {
            "verdict": "keep", "date": "2026-08-22",
            "evidence": "skills/a-skill/references/eval-result.md",
        })
        # what it just wrote must itself pass this script's own check.
        self.assertEqual(eval_status.main([]), 0)

    def test_record_defaults_date_to_today(self):
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "improve",
            "--evidence", "skills/a-skill/references/eval-result.md",
        ])
        self.assertEqual(rc, 0)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"]["date"], datetime.date.today().isoformat())

    def test_record_refuses_nonexistent_skill(self):
        rc = eval_status.main([
            "--record", "no-such-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/eval-result.md",
        ])
        self.assertEqual(rc, 2)
        # nothing written -- the record is untouched.
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertNotIn("no-such-skill", record)

    def test_record_refuses_unevaluated_as_a_verdict_to_record(self):
        """unevaluated is the record's own default for a never-touched
        entry, not something --record should ever be asked to write --
        see do_record's own docstring for why."""
        with self.assertRaises(SystemExit):
            # argparse itself refuses: "unevaluated" is not in --verdict's
            # choices (RECORDABLE_VERDICTS excludes it).
            eval_status.main([
                "--record", "a-skill", "--verdict", "unevaluated",
                "--evidence", "skills/a-skill/references/eval-result.md",
            ])

    def test_record_refuses_missing_evidence_file(self):
        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "keep",
            "--evidence", "skills/a-skill/references/does-not-exist.md",
        ])
        self.assertEqual(rc, 2)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["a-skill"]["verdict"], "unevaluated")

    def test_record_requires_verdict(self):
        rc = eval_status.main([
            "--record", "a-skill",
            "--evidence", "skills/a-skill/references/eval-result.md",
        ])
        self.assertEqual(rc, 2)

    def test_record_preserves_other_entries(self):
        # add a second, already-recorded skill directly, bypassing --record,
        # to prove recording "a-skill" doesn't clobber it.
        (self.tmp / "skills" / "b-skill").mkdir()
        doc = eval_status.load_full_doc(eval_status.RECORD_PATH)
        doc["skills"]["b-skill"] = {"verdict": "keep", "date": "2020-01-01", "evidence": "README.md"}
        eval_status.dump_record(doc, eval_status.RECORD_PATH)

        rc = eval_status.main([
            "--record", "a-skill", "--verdict", "drop",
            "--evidence", "skills/a-skill/references/eval-result.md",
            "--date", "2026-08-22",
        ])
        self.assertEqual(rc, 0)
        record = eval_status.load_record(eval_status.RECORD_PATH)
        self.assertEqual(record["b-skill"]["verdict"], "keep")
        self.assertEqual(record["a-skill"]["verdict"], "drop")


if __name__ == "__main__":
    unittest.main()

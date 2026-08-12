from __future__ import annotations

import importlib.util
import io
import re
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "check_orphan_skills.py"
SPEC = importlib.util.spec_from_file_location("check_orphan_skills", SCRIPT_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)

WORKFLOW_PATH = Path(__file__).parents[1] / ".github" / "workflows" / "validate.yml"

ROSTER_TEXT = """\
close-the-loop
create-skill

[benched]
loop-contract   # jonhill90/skills#133: ship public opt-in
"""


def make_skills(root: Path, names: list[str]) -> Path:
    skills_dir = root / "skills"
    for name in names:
        skill_dir = skills_dir / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: test skill.\n---\n\nBody.\n",
            encoding="utf-8",
        )
    return skills_dir


class ParseRosterTests(unittest.TestCase):
    def test_splits_rostered_and_benched(self):
        rostered, benched = checker.parse_roster(ROSTER_TEXT)
        self.assertEqual(rostered, {"close-the-loop", "create-skill"})
        self.assertEqual(benched, {"loop-contract"})

    def test_ignores_comments_and_blank_lines(self):
        text = "# a comment\n\nclose-the-loop\n"
        rostered, benched = checker.parse_roster(text)
        self.assertEqual(rostered, {"close-the-loop"})
        self.assertEqual(benched, set())


class FindOrphansTests(unittest.TestCase):
    def test_rostered_skill_is_not_an_orphan(self):
        orphans = checker.find_orphans({"a"}, rostered={"a"}, benched=set())
        self.assertEqual(orphans, [])

    def test_benched_skill_is_not_an_orphan(self):
        # Test 3: a benched skill must not be reported.
        orphans = checker.find_orphans({"a"}, rostered=set(), benched={"a"})
        self.assertEqual(orphans, [])

    def test_unrostered_unbenched_skill_is_an_orphan(self):
        # Test 1: a skill absent from a visible roster is reported.
        orphans = checker.find_orphans({"a", "b"}, rostered={"a"}, benched=set())
        self.assertEqual(orphans, ["b"])


class LoadRosterTests(unittest.TestCase):
    def test_local_path_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            roster = Path(tmp) / "default-skills.txt"
            roster.write_text(ROSTER_TEXT, encoding="utf-8")
            text, source = checker.load_roster(str(roster), None)
            self.assertEqual(text, ROSTER_TEXT)
            self.assertIn(str(roster), source)

    def test_missing_local_path_is_unreachable(self):
        text, source = checker.load_roster("/no/such/file", None)
        self.assertIsNone(text)
        self.assertIn("not found", source)

    def test_no_path_and_no_url_is_unreachable(self):
        text, source = checker.load_roster(None, None)
        self.assertIsNone(text)

    def test_network_failure_is_unreachable(self):
        def failing_opener(url, timeout=10):
            raise urllib.error.URLError("simulated network failure")

        text, source = checker.load_roster(
            None, "https://example.invalid/default-skills.txt", opener=failing_opener
        )
        self.assertIsNone(text)
        self.assertIn("simulated network failure", source)


class RunTests(unittest.TestCase):
    def run_checker(self, names: list[str], roster_path: str | None):
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = make_skills(Path(tmp), names)
            out = io.StringIO()
            code = checker.run(skills_dir, roster_path, None, out=out)
            return code, out.getvalue()

    def test_1_orphan_reported_when_roster_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            roster = Path(tmp) / "default-skills.txt"
            roster.write_text(ROSTER_TEXT, encoding="utf-8")
            code, output = self.run_checker(
                ["close-the-loop", "an-orphan-skill"], str(roster)
            )
        self.assertEqual(code, 1)
        self.assertIn("  an-orphan-skill", output)
        self.assertNotIn("  close-the-loop", output)

    def test_2_unreachable_roster_says_so_and_never_claims_clean(self):
        # Test 2: with no roster reachable, the output says so and does
        # NOT claim a clean result -- the honesty property #162 is about.
        code, output = self.run_checker(["close-the-loop"], "/no/such/roster.txt")
        self.assertEqual(code, 2)
        self.assertIn("UNREACHABLE", output)
        self.assertNotIn("CLEAN", output)

    def test_3_benched_skill_not_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            roster = Path(tmp) / "default-skills.txt"
            roster.write_text(ROSTER_TEXT, encoding="utf-8")
            code, output = self.run_checker(
                ["close-the-loop", "loop-contract"], str(roster)
            )
        self.assertEqual(code, 0)
        self.assertIn("CLEAN", output)

class OrphanCheckNeverFailsBuildTests(unittest.TestCase):
    def test_4_ci_job_is_advisory_only(self):
        # Test 4: the check never fails the build. Verified at the CI
        # wiring, not the script's own exit code -- the script legitimately
        # returns non-zero (1 orphan found, 2 could not check) so that
        # exit code stays a meaningful, distinguishable signal; it is the
        # workflow step that must not let that fail the job.
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        match = re.search(
            r"orphan-check:.*?(?=\n  \S|\Z)", workflow, re.DOTALL
        )
        self.assertIsNotNone(match, "orphan-check job not found in validate.yml")
        job_text = match.group(0)
        self.assertIn("continue-on-error: true", job_text)
        self.assertIn("check_orphan_skills.py", job_text)


if __name__ == "__main__":
    unittest.main()

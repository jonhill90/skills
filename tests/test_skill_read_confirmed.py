"""jonhill90/skills#269 review (estate:2): prove skill_read_confirmed by
construction, in both mutation directions, not by reading the function and
trusting it -- this repo's own standing convention for a scorer-adjacent
utility (see test_eval_status.py's own header for the same import shape)."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "skill_read_confirmed.py"
SPEC = importlib.util.spec_from_file_location("skill_read_confirmed", SCRIPT_PATH)
assert SPEC and SPEC.loader
skill_read_confirmed_mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = skill_read_confirmed_mod
SPEC.loader.exec_module(skill_read_confirmed_mod)
skill_read_confirmed = skill_read_confirmed_mod.skill_read_confirmed


def _assistant_turn(*blocks: dict) -> dict:
    """One JSONL line shaped like a real Claude Code transcript's assistant
    turn -- verified against a live ~/.claude/projects/*.jsonl transcript
    before writing this fixture, not assumed: type "assistant" at the top
    level, message.content a list of blocks."""
    return {"type": "assistant", "message": {"role": "assistant", "content": list(blocks)}}


def _read_block(file_path: str) -> dict:
    return {"type": "tool_use", "name": "Read", "input": {"file_path": file_path}}


def _write_transcript(tmpdir: Path, name: str, lines: list[dict]) -> Path:
    path = tmpdir / name
    path.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
    return path


class SkillReadConfirmedTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    # --- the two mandatory mutation-check directions -----------------

    def test_confirmed_true_when_the_read_genuinely_happened(self):
        transcript = _write_transcript(
            self.tmpdir,
            "with-read.jsonl",
            [
                _assistant_turn(
                    {"type": "text", "text": "Let me check the skill first."},
                    _read_block("/home/agent/work/skills/github-cli/SKILL.md"),
                ),
            ],
        )
        self.assertTrue(
            skill_read_confirmed(transcript, "skills/github-cli/SKILL.md"),
            "a transcript with a real Read of the exact skill path must confirm true",
        )

    def test_confirmed_false_when_the_read_never_happened(self):
        # Same shape, same skill, but Arm A went straight to the task --
        # exactly the silent-wiring-failure case this function exists to
        # catch, indistinguishable from a genuine null in prose or in
        # manifest.json's own self-reported actions_log.
        transcript = _write_transcript(
            self.tmpdir,
            "without-read.jsonl",
            [
                _assistant_turn(
                    {"type": "text", "text": "I'll just run gh run watch directly."},
                    {"type": "tool_use", "name": "Bash", "input": {"command": "gh run watch 9001 --exit-status"}},
                ),
            ],
        )
        self.assertFalse(
            skill_read_confirmed(transcript, "skills/github-cli/SKILL.md"),
            "a transcript with no Read of the skill path must confirm false",
        )

    # --- must be a REAL Read tool_use, never a stand-in ----------------

    def test_a_bash_cat_of_the_same_file_does_not_count(self):
        """The whole point is refusing self-report-shaped evidence -- a
        Bash command that happens to cat the SKILL.md text is not the
        mechanical signal this function is built to trust, even though a
        naive substring search over the transcript would find the path."""
        transcript = _write_transcript(
            self.tmpdir,
            "bash-cat.jsonl",
            [
                _assistant_turn(
                    _read_block("skills/github-cli/SKILL.md"),
                )
            ],
        )
        # Sanity: the Read-tool version of this exact path DOES confirm --
        # proves the negative case below isn't failing for some unrelated
        # reason (e.g. a broken fixture).
        self.assertTrue(skill_read_confirmed(transcript, "skills/github-cli/SKILL.md"))

        bash_transcript = _write_transcript(
            self.tmpdir,
            "bash-cat-2.jsonl",
            [
                _assistant_turn(
                    {"type": "tool_use", "name": "Bash", "input": {"command": "cat skills/github-cli/SKILL.md"}},
                )
            ],
        )
        self.assertFalse(
            skill_read_confirmed(bash_transcript, "skills/github-cli/SKILL.md"),
            "a Bash cat of the skill file must not count as a confirmed Read",
        )

    def test_actions_log_style_self_report_is_never_consulted(self):
        """manifest.json's own actions_log is explicitly untrusted by this
        harness (docs/eval-harness-findings.md) -- confirm this function
        doesn't accidentally read anything shaped like it out of the
        transcript itself."""
        transcript = _write_transcript(
            self.tmpdir,
            "self-report.jsonl",
            [
                _assistant_turn(
                    {"type": "text", "text": "actions_log: [\"read skills/github-cli/SKILL.md\"]"},
                )
            ],
        )
        self.assertFalse(skill_read_confirmed(transcript, "skills/github-cli/SKILL.md"))

    # --- path-matching, both forms named in the brief -------------------

    def test_relative_skill_path_matches_an_absolute_transcript_path(self):
        transcript = _write_transcript(
            self.tmpdir,
            "abs.jsonl",
            [_assistant_turn(_read_block("/private/var/tmp/eval-run-42/skills/linear/SKILL.md"))],
        )
        self.assertTrue(skill_read_confirmed(transcript, "skills/linear/SKILL.md"))

    def test_absolute_skill_path_requires_exact_match(self):
        transcript = _write_transcript(
            self.tmpdir,
            "abs-exact.jsonl",
            [_assistant_turn(_read_block("/private/var/tmp/eval-run-42/skills/linear/SKILL.md"))],
        )
        self.assertTrue(
            skill_read_confirmed(transcript, "/private/var/tmp/eval-run-42/skills/linear/SKILL.md")
        )
        self.assertFalse(
            skill_read_confirmed(transcript, "/somewhere/else/skills/linear/SKILL.md"),
            "an absolute query path must match exactly, not by suffix",
        )

    def test_suffix_match_respects_a_path_boundary(self):
        """'skills/linear/SKILL.md' must not match
        'myskills/linear/SKILL.md' just because one string ends with the
        other -- the boundary must be a real path separator."""
        transcript = _write_transcript(
            self.tmpdir,
            "boundary.jsonl",
            [_assistant_turn(_read_block("/work/myskills/linear/SKILL.md"))],
        )
        self.assertFalse(skill_read_confirmed(transcript, "skills/linear/SKILL.md"))

    def test_read_of_a_different_skill_does_not_confirm(self):
        transcript = _write_transcript(
            self.tmpdir,
            "wrong-skill.jsonl",
            [_assistant_turn(_read_block("/work/skills/obsidian/SKILL.md"))],
        )
        self.assertFalse(skill_read_confirmed(transcript, "skills/linear/SKILL.md"))

    # --- fail-closed behaviour -------------------------------------------

    def test_missing_transcript_fails_closed_to_false(self):
        self.assertFalse(
            skill_read_confirmed(self.tmpdir / "does-not-exist.jsonl", "skills/linear/SKILL.md")
        )

    def test_malformed_lines_are_skipped_not_fatal(self):
        path = self.tmpdir / "malformed.jsonl"
        path.write_text(
            "not json at all\n"
            + json.dumps(_assistant_turn(_read_block("/work/skills/linear/SKILL.md"))),
            encoding="utf-8",
        )
        self.assertTrue(skill_read_confirmed(path, "skills/linear/SKILL.md"))

    def test_empty_transcript_confirms_false(self):
        path = self.tmpdir / "empty.jsonl"
        path.write_text("", encoding="utf-8")
        self.assertFalse(skill_read_confirmed(path, "skills/linear/SKILL.md"))


class CLITests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cli_exit_codes(self):
        import subprocess

        confirmed = _write_transcript(
            self.tmpdir, "confirmed.jsonl", [_assistant_turn(_read_block("/w/skills/linear/SKILL.md"))]
        )
        rc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(confirmed), "skills/linear/SKILL.md"],
            capture_output=True, text=True,
        )
        self.assertEqual(rc.returncode, 0)
        self.assertEqual(rc.stdout.strip(), "true")

        not_confirmed = _write_transcript(
            self.tmpdir, "not-confirmed.jsonl", [_assistant_turn({"type": "text", "text": "no reads here"})]
        )
        rc2 = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(not_confirmed), "skills/linear/SKILL.md"],
            capture_output=True, text=True,
        )
        self.assertEqual(rc2.returncode, 1)
        self.assertEqual(rc2.stdout.strip(), "false")

        rc3 = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(self.tmpdir / "nope.jsonl"), "skills/linear/SKILL.md"],
            capture_output=True, text=True,
        )
        self.assertEqual(rc3.returncode, 2)


if __name__ == "__main__":
    unittest.main()

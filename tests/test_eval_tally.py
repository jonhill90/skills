from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "eval_tally.py"
SPEC = importlib.util.spec_from_file_location("eval_tally", SCRIPT_PATH)
assert SPEC and SPEC.loader
eval_tally = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = eval_tally
SPEC.loader.exec_module(eval_tally)


class EvalTallyTests(unittest.TestCase):
    def _write(self, root: Path, skill: str, text: str) -> None:
        references = root / skill / "references"
        references.mkdir(parents=True, exist_ok=True)
        (references / "eval-result.md").write_text(text, encoding="utf-8")

    def test_first_line_wins_when_a_prior_pass_is_kept(self) -> None:
        """The exact trap jonhill90/skills#294 names: a file keeps a
        superseded verdict for the record. It must still be marked
        "Previous verdict:", not "Verdict:", to count only once."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(
                root, "alpha",
                "# Eval result\n\n**Verdict: improve (n=1, second pass)**\n\n"
                "## Prior pass\n\n**Previous verdict: could_not_measure**\n",
            )
            self.assertEqual(eval_tally.find_verdict_problems(root), [])
            self.assertEqual(dict(eval_tally.tally(root)), {"improve": 1})

    def test_two_authoritative_lines_is_a_problem(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(
                root, "alpha",
                "# Eval result\n\n**Verdict: keep**\n\n**Verdict: drop**\n",
            )
            problems = eval_tally.find_verdict_problems(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("2 \"Verdict:\" lines found", problems[0])

    def test_zero_authoritative_lines_is_a_problem(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, "alpha", "# Eval result\n\nnothing to see here.\n")
            problems = eval_tally.find_verdict_problems(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("no authoritative", problems[0])

    def test_tally_matches_the_verdict_tokens_present(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, "alpha", "# Eval result\n\n**Verdict: keep**\n")
            self._write(root, "beta", "# Eval result\n\n**Verdict: keep**\n")
            self._write(root, "gamma", "# Eval result\n\n**Verdict: drop**\n")
            self.assertEqual(eval_tally.find_verdict_problems(root), [])
            self.assertEqual(dict(eval_tally.tally(root)), {"keep": 2, "drop": 1})

    def test_real_repository_tally_is_3_20_3_11_3_1(self) -> None:
        """jonhill90/skills#296's own named figure, measured against the
        actual tree this test ships with -- not a synthetic fixture. The
        26 `could_not_measure` of #294 split three ways: 3 genuinely blind,
        20 clean null results, 3 inadequate scenarios."""
        skills_root = Path(__file__).resolve().parents[1] / "skills"
        self.assertEqual(eval_tally.find_verdict_problems(skills_root), [])
        counts = eval_tally.tally(skills_root)
        self.assertEqual(
            dict(counts),
            {
                "could_not_measure": 3,
                "no_effect_observed": 20,
                "scenario_inadequate": 3,
                "improve": 11,
                "keep": 3,
                "drop": 1,
            },
        )
        self.assertEqual(sum(counts.values()), 41)

    def test_main_exits_nonzero_when_a_file_has_two_verdict_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(
                root, "alpha",
                "# Eval result\n\n**Verdict: keep**\n\n**Verdict: drop**\n",
            )
            original_root = eval_tally.SKILLS_ROOT
            eval_tally.SKILLS_ROOT = root
            try:
                self.assertEqual(eval_tally.main([]), 1)
            finally:
                eval_tally.SKILLS_ROOT = original_root

    def test_main_exits_zero_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, "alpha", "# Eval result\n\n**Verdict: keep**\n")
            original_root = eval_tally.SKILLS_ROOT
            eval_tally.SKILLS_ROOT = root
            try:
                self.assertEqual(eval_tally.main([]), 0)
            finally:
                eval_tally.SKILLS_ROOT = original_root


if __name__ == "__main__":
    unittest.main()

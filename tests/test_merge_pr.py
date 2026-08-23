"""jonhill90/skills#256: mutation-check for merge_pr.py's own two-gate
merge wrapper -- the same "a guard nobody has watched fail is not a guard"
bar `test_pr_verdict.py` already applies to the gate this wraps, applied
here to the four directions #256 itself names:

  1. CI red                                      -> refuses, never merges
  2. CI green, no verdict                        -> refuses, never merges
  3. CI green, same-lane verdict                  -> refuses, never merges
  4. CI green, genuine cross-lane verdict         -> merges

Every fixture supplies fake `ci_green`/`pr_verdict`/`merge` callables
through `run`'s own seams -- no real `gh` subprocess, no real network,
matching `test_pr_verdict.py`'s own synthetic-fixture discipline. Each
fake `merge` records whether it was called at all, so a case that must
refuse is checked for "never even attempted a merge", not just "exited
non-zero" -- the failure mode this gate exists to prevent is a false
PASS reaching `gh pr merge`, so the assertion has to watch that call
site directly, not just the return value."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import merge_pr as mp  # noqa: E402

HEAD = "a" * 40


def _spy_merge(should_succeed=True, detail="merged ok"):
    calls = []

    def _merge(repo, number):
        calls.append((repo, number))
        return should_succeed, detail

    _merge.calls = calls
    return _merge


class MutationCheckFourDirections(unittest.TestCase):
    """The exact four cases #256 names, each demonstrated in the direction
    that matters -- a false MERGE is the expensive one, so every refusing
    case here also asserts the merge spy was never called, not merely that
    the decision string says refused."""

    def test_1_ci_red_refuses_without_calling_verdict_or_merge(self):
        verdict_calls = []

        def _pr_verdict(repo, number):
            verdict_calls.append((repo, number))
            return 0, {"decision": "approved", "detail": "should never be reached"}

        merge = _spy_merge()
        result = mp.run(
            "jonhill90/skills", 1,
            ci_green=lambda repo, number: (False, "1 check(s), buckets: ['fail']"),
            pr_verdict=_pr_verdict,
            merge=merge,
        )
        self.assertEqual(result["decision"], "ci-not-green")
        self.assertEqual(verdict_calls, [], "pr_verdict must not run when CI is red")
        self.assertEqual(merge.calls, [], "gh pr merge must never be attempted when CI is red")

    def test_2_ci_green_no_verdict_refuses_without_merging(self):
        merge = _spy_merge()
        result = mp.run(
            "jonhill90/skills", 1,
            ci_green=lambda repo, number: (True, "1 check(s) green"),
            pr_verdict=lambda repo, number: (2, {"decision": "none", "detail": "no comment on this PR carries a Verdict: line"}),
            merge=merge,
        )
        self.assertEqual(result["decision"], "not-approved")
        self.assertIn("none", result["detail"])
        self.assertEqual(merge.calls, [], "gh pr merge must never be attempted with no verdict on record")

    def test_3_ci_green_same_lane_verdict_refuses_without_merging(self):
        merge = _spy_merge()
        result = mp.run(
            "jonhill90/skills", 1,
            ci_green=lambda repo, number: (True, "1 check(s) green"),
            pr_verdict=lambda repo, number: (
                3,
                {"decision": "unknown", "detail": f"approved comment by @build-5 -- reviewer lane 'build-5' is the same as the PR's own Author-Lane 'build-5' -- self-review"},
            ),
            merge=merge,
        )
        self.assertEqual(result["decision"], "not-approved")
        self.assertIn("self-review", result["detail"])
        self.assertEqual(merge.calls, [], "gh pr merge must never be attempted on a same-lane (self-review) verdict")

    def test_4_ci_green_genuine_cross_lane_verdict_merges(self):
        merge = _spy_merge(should_succeed=True, detail="Squashed and merged")
        result = mp.run(
            "jonhill90/skills", 1,
            ci_green=lambda repo, number: (True, "2 check(s) green"),
            pr_verdict=lambda repo, number: (
                0,
                {"decision": "approved", "detail": f"approved comment by @build-5, Review-Lane build-5, Reviewed-SHA {HEAD} matches current head"},
            ),
            merge=merge,
        )
        self.assertEqual(result["decision"], "merged")
        self.assertEqual(merge.calls, [("jonhill90/skills", 1)], "gh pr merge must be attempted exactly once when both gates pass")


class ExitCodesTests(unittest.TestCase):
    """`main`'s exit code is the caller-facing contract (`pr_verdict.py`'s
    own "decide by exit code alone" pattern) -- checked directly against
    `_EXIT_FOR_DECISION` rather than trusting the mapping exists."""

    def test_exit_codes_cover_every_decision(self):
        self.assertEqual(mp._EXIT_FOR_DECISION["merged"], 0)
        self.assertEqual(mp._EXIT_FOR_DECISION["ci-not-green"], 1)
        self.assertEqual(mp._EXIT_FOR_DECISION["not-approved"], 2)
        self.assertEqual(mp._EXIT_FOR_DECISION["merge-failed"], 3)


class MergeFailureTests(unittest.TestCase):
    """Both gates can pass and `gh pr merge` can still fail (conflict,
    branch protection) -- that must be reported distinctly from either
    gate refusing, not folded into a generic non-zero exit."""

    def test_both_gates_pass_but_merge_command_fails(self):
        merge = _spy_merge(should_succeed=False, detail="branch protection: review required")
        result = mp.run(
            "jonhill90/skills", 1,
            ci_green=lambda repo, number: (True, "1 check(s) green"),
            pr_verdict=lambda repo, number: (0, {"decision": "approved", "detail": "approved"}),
            merge=merge,
        )
        self.assertEqual(result["decision"], "merge-failed")
        self.assertEqual(merge.calls, [("jonhill90/skills", 1)])


if __name__ == "__main__":
    unittest.main()

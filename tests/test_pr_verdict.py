"""jonhill90/skills#254: mutation-check for pr_verdict.py's comment-verdict
gate -- the same "a guard nobody has watched fail is not a guard" bar
`test_check_skill_install.py` already applies to this repository's other
mechanical gate, applied here to the four directions #254 itself names:

  1. same-lane verdict                          -> must FAIL (unknown)
  2. genuine cross-lane verdict at current head  -> must PASS (approved)
  3. cross-lane verdict against a stale SHA      -> must FAIL (unknown)
  4. no verdict at all                           -> must FAIL (none)

Every fixture supplies a fake `gh pr view` payload through `resolve`'s own
`gh_pr_view` seam -- no real subprocess, no real network, matching this
repository's other scripts/*.py test files (`test_check_skill_install.py`'s
own synthetic-fixture discipline)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pr_verdict as pv  # noqa: E402

HEAD = "a" * 40
OLD = "b" * 40


def _payload(*, body="Author-Lane: build-2\n", comments=None, head=HEAD):
    return {"headRefOid": head, "body": body, "comments": comments or []}


def _comment(text, author="jonhill90"):
    return {"author": {"login": author}, "body": text}


def _resolve(payload):
    return pv.resolve("jonhill90/skills", 1, gh_pr_view=lambda repo, number: payload)


class MutationCheckFourDirections(unittest.TestCase):
    """The exact four cases #254 names, each demonstrated in the direction
    that matters -- a false PASS is the expensive one, so every failing
    case here is checked for the SPECIFIC reason, not just a non-zero
    result, so a future change that returns 'unknown' for the wrong reason
    still gets caught."""

    def test_1_same_lane_verdict_fails(self):
        payload = _payload(
            body="Author-Lane: build-5\n",
            comments=[_comment(f"Verdict: APPROVE\nReview-Lane: build-5\nReviewed-SHA: {HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("self-review", result["detail"])

    def test_2_genuine_cross_lane_verdict_at_current_head_passes(self):
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment(f"Verdict: APPROVE\nReview-Lane: build-5\nReviewed-SHA: {HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "approved")

    def test_3_cross_lane_verdict_against_stale_sha_fails(self):
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment(f"Verdict: APPROVE\nReview-Lane: build-5\nReviewed-SHA: {OLD}\n")],
            head=HEAD,
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("stale", result["detail"])

    def test_4_no_verdict_at_all_fails(self):
        payload = _payload(body="Author-Lane: build-2\n", comments=[])
        result = _resolve(payload)
        self.assertEqual(result["decision"], "none")


class BlankReviewLaneSelfApprovalBypass(unittest.TestCase):
    """Security regression, filed and fixed the same day it was found: a
    BLANK `Review-Lane:` value let `_REVIEW_LANE_LINE_RE`'s post-colon
    `\\s*` consume the line break and capture the NEXT line's text
    (`Reviewed-SHA: ...`) instead of matching empty. That non-empty
    garbage never equals a real `Author-Lane:` value, so the same-lane
    self-review check below it silently never fired -- a same-lane author
    posting a comment with a blank `Review-Lane:` trailer got treated as
    a valid, different reviewer and the PR resolved `approved`. This
    exact shape -- blank trailer, same lane as Author-Lane, real head SHA
    on the very next line -- must never again resolve to anything but
    `unknown`."""

    def test_blank_review_lane_same_author_lane_is_not_approved(self):
        payload = _payload(
            body="Author-Lane: build-3\n",
            comments=[_comment(f"Verdict: APPROVE\nAuthor-Lane: build-3\nReview-Lane: \nReviewed-SHA: {HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("Review-Lane", result["detail"])

    def test_blank_review_lane_does_not_capture_the_next_line(self):
        # Direct regression on the regex itself, not just resolve()'s
        # outcome -- pins the exact failure mode build-3 reported so a
        # future refactor of the pattern can't silently reopen it while
        # still passing the resolve()-level test above by coincidence.
        body = "Verdict: APPROVE\nAuthor-Lane: build-3\nReview-Lane: \nReviewed-SHA: abc123\n"
        value = pv._parse_trailer(pv._REVIEW_LANE_LINE_RE, body)
        self.assertIsNone(value)


class BlankReviewedShaAlsoBypassed(unittest.TestCase):
    """jonhill90/skills#259: #260 fixed Review-Lane:/Author-Lane: but its
    commit message asserted `_REVIEWED_SHA_RE` "already only matches
    `[A-Za-z0-9]+` so it never had this bug" -- false. The mandatory `+`
    only stops it matching on the BLANK trailer's own (empty) line; the
    leading `\\s*` still crosses the newline and re-anchors on the NEXT
    line, where `[A-Za-z0-9]+` captures that line's leading alnum run as
    if it were the SHA. Because the capture is alnum-only (unlike the
    free-text `(.*)$` capture Review-Lane:/Author-Lane: use), the bug only
    fires when everything on the next line, after that captured run, is
    itself blank/whitespace to end-of-line -- e.g. the next line is a
    bare alnum token with no other punctuation. A raw SHA quoted on its
    own line, with no `Reviewed-SHA:` label, is exactly that shape, and
    is exactly what makes this a live self-approval bypass: if that raw
    line happens to equal the PR's real head SHA, the blank trailer is
    silently treated as a MATCHING one."""

    def test_blank_reviewed_sha_does_not_capture_a_bare_alnum_next_line(self):
        body = "Verdict: APPROVE\nReviewed-SHA:\nabc123def\n"
        value = pv._parse_trailer(pv._REVIEWED_SHA_RE, body)
        self.assertIsNone(value)

    def test_blank_reviewed_sha_followed_by_the_real_head_sha_bare_is_not_approved(self):
        # The security-relevant shape: Reviewed-SHA: is left blank, but the
        # very next line happens to BE the PR's real current head SHA
        # (e.g. pasted in without its label). A real approval still
        # requires the `Reviewed-SHA:` trailer itself to carry the value
        # -- a blank trailer must never be rescued by coincidental text
        # sitting on the following line.
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment(f"Verdict: APPROVE\nReview-Lane: build-5\nReviewed-SHA:\n{HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("Reviewed-SHA", result["detail"])


class TrailerRegexShapeCoverage(unittest.TestCase):
    """The real trailer shapes a comment or PR body can carry, run through
    all three patterns directly (not just the one blank-then-trailer shape
    each bug report happened to quote): a normal value, a blank value
    immediately followed by another trailer line, a blank value at the
    very end of the body (no next line to wrongly capture), trailing
    horizontal whitespace after a real value, and CRLF line endings."""

    # Reviewed-SHA's capture is restricted to `[A-Za-z0-9]+` (no hyphen),
    # unlike the free-text Review-Lane:/Author-Lane: values -- each
    # trailer gets its own valid sample value so every pattern is
    # exercised against a shape it actually accepts.
    _PATTERNS = {
        "Review-Lane": (pv._REVIEW_LANE_LINE_RE, "build-9"),
        "Author-Lane": (pv._AUTHOR_LANE_LINE_RE, "build-9"),
        "Reviewed-SHA": (pv._REVIEWED_SHA_RE, "abc123"),
    }

    def test_value_present_is_captured(self):
        for name, (pattern, value) in self._PATTERNS.items():
            with self.subTest(trailer=name):
                body = f"{name}: {value}\n"
                self.assertEqual(pv._parse_trailer(pattern, body), value)

    # The next trailer line must never be the SAME trailer name as the one
    # under test -- "Reviewed-SHA:\nReviewed-SHA: <real sha>\n" would let
    # `.search()` legitimately find the second, well-formed occurrence and
    # return it, which is correct behaviour, not a regression. Each blank
    # trailer is instead followed by a genuinely different trailer, the
    # exact shape both #259 and #260 describe.
    _NEXT_LINE = {
        "Review-Lane": f"Reviewed-SHA: {HEAD}",
        "Author-Lane": f"Reviewed-SHA: {HEAD}",
        "Reviewed-SHA": "Author-Lane: build-2",
    }

    def test_blank_value_followed_by_another_trailer_is_missing(self):
        for name, (pattern, _value) in self._PATTERNS.items():
            with self.subTest(trailer=name):
                body = f"{name}:\n{self._NEXT_LINE[name]}\n"
                self.assertIsNone(pv._parse_trailer(pattern, body))

    def test_blank_value_at_end_of_body_is_missing(self):
        for name, (pattern, _value) in self._PATTERNS.items():
            with self.subTest(trailer=name):
                body = f"Verdict: APPROVE\n{name}:\n"
                self.assertIsNone(pv._parse_trailer(pattern, body))

    def test_trailing_horizontal_whitespace_is_stripped(self):
        for name, (pattern, value) in self._PATTERNS.items():
            with self.subTest(trailer=name):
                body = f"{name}: {value}   \n"
                self.assertEqual(pv._parse_trailer(pattern, body), value)

    def test_crlf_line_endings_still_match(self):
        for name, (pattern, value) in self._PATTERNS.items():
            with self.subTest(trailer=name):
                body = f"{name}: {value}\r\n"
                self.assertEqual(pv._parse_trailer(pattern, body), value)

    def test_crlf_blank_value_followed_by_another_trailer_is_missing(self):
        for name, (pattern, _value) in self._PATTERNS.items():
            with self.subTest(trailer=name):
                body = f"{name}:\r\n{self._NEXT_LINE[name]}\r\n"
                self.assertIsNone(pv._parse_trailer(pattern, body))


class ExitCodesMatchDecision(unittest.TestCase):
    """A caller gates on the exit code alone (this module's own docstring
    contract) -- prove the mapping, not just resolve()'s return value."""

    def test_approved_is_zero(self):
        self.assertEqual(pv._EXIT_FOR_DECISION["approved"], 0)

    def test_rejected_is_nonzero(self):
        self.assertNotEqual(pv._EXIT_FOR_DECISION["rejected"], 0)

    def test_none_is_nonzero(self):
        self.assertNotEqual(pv._EXIT_FOR_DECISION["none"], 0)

    def test_unknown_is_nonzero(self):
        self.assertNotEqual(pv._EXIT_FOR_DECISION["unknown"], 0)

    def test_all_four_decisions_map_to_distinct_codes(self):
        codes = list(pv._EXIT_FOR_DECISION.values())
        self.assertEqual(len(codes), len(set(codes)))


class IndependenceEdgeCases(unittest.TestCase):
    def test_missing_author_lane_refuses_even_with_a_clean_review(self):
        payload = _payload(
            body="no trailer here\n",
            comments=[_comment(f"Verdict: APPROVE\nReview-Lane: build-5\nReviewed-SHA: {HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("Author-Lane", result["detail"])

    def test_missing_review_lane_refuses(self):
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment(f"Verdict: APPROVE\nReviewed-SHA: {HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("Review-Lane", result["detail"])

    def test_missing_reviewed_sha_refuses(self):
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment("Verdict: APPROVE\nReview-Lane: build-5\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("Reviewed-SHA", result["detail"])

    def test_rejected_cross_lane_at_current_head_is_rejected_not_approved(self):
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment(f"Verdict: REQUEST CHANGES\nReview-Lane: build-5\nReviewed-SHA: {HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "rejected")

    def test_later_comment_supersedes_an_earlier_self_approval_attempt(self):
        """agent-supervisor#196's own rule, ported: a reviewer who reconsiders
        must have the LATER decision win, not an earlier draft -- exercised
        here across two independent lanes rather than one reviewer's own
        redraft, since that is the shape this repo's estate actually
        produces (a second lane re-reviewing after the first one's verdict
        went stale)."""
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[
                _comment(f"Verdict: REQUEST CHANGES\nReview-Lane: build-4\nReviewed-SHA: {HEAD}\n"),
                _comment(f"Verdict: APPROVE\nReview-Lane: build-5\nReviewed-SHA: {HEAD}\n"),
            ],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "approved")

    def test_negated_decision_text_is_not_read_as_approval(self):
        """agent-supervisor#198's own regression, ported directly."""
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment(f"Verdict: NOT APPROVED\nReview-Lane: build-5\nReviewed-SHA: {HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("not recognised", result["detail"])

    def test_verdict_quoted_inside_a_fenced_code_block_does_not_count(self):
        """agent-supervisor#192's own regression, ported directly -- an
        example, not a real verdict."""
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment("Here's the format:\n```\nVerdict: APPROVE\nReview-Lane: build-5\n```\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "none")

    def test_conflicting_verdict_lines_in_one_comment_refuse(self):
        """agent-supervisor#196's own regression, ported directly -- two
        DIFFERING decisions in one comment must not pick either one."""
        payload = _payload(
            body="Author-Lane: build-2\n",
            comments=[_comment(f"Verdict: APPROVE\nVerdict: REQUEST CHANGES\nReview-Lane: build-5\nReviewed-SHA: {HEAD}\n")],
        )
        result = _resolve(payload)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("conflicting", result["detail"])


class GhReadFailureFailsClosed(unittest.TestCase):
    def test_gh_exception_resolves_to_unknown_not_a_crash(self):
        def boom(repo, number):
            raise RuntimeError("network unreachable")

        result = pv.resolve("jonhill90/skills", 1, gh_pr_view=boom)
        self.assertEqual(result["decision"], "unknown")
        self.assertIn("gh pr view failed", result["detail"])

    def test_missing_head_sha_in_payload_resolves_to_unknown(self):
        result = pv.resolve(
            "jonhill90/skills", 1,
            gh_pr_view=lambda repo, number: {"body": "", "comments": []},
        )
        self.assertEqual(result["decision"], "unknown")


class CliExitCode(unittest.TestCase):
    """The actual `main()` entry point, not just `resolve()` -- proves the
    argparse wiring and the exit-code mapping together, the shape a real
    caller (a shell `if` gating a merge) depends on."""

    def test_main_returns_zero_for_approved(self):
        import io
        import contextlib

        original = pv._default_gh_pr_view
        pv._default_gh_pr_view = lambda repo, number: _payload(
            comments=[_comment(f"Verdict: APPROVE\nReview-Lane: build-5\nReviewed-SHA: {HEAD}\n")],
        )
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = pv.main(["--repo", "jonhill90/skills", "--number", "1"])
        finally:
            pv._default_gh_pr_view = original
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Read a PR's own comments and decide whether it carries an independent,
current APPROVE — jonhill90/skills#254's port of the comment-verdict gate
`jonhill90/agent-supervisor` already runs (`scripts/supervisor/verdict.py`,
`scripts/supervisor/verdict-independence.sh`).

Why this exists: every lane in this estate pushes through one shared
GitHub login, so `gh pr review --approve` is refused as self-review no
matter which lane is asking, and GitHub's own review state can never
name which lane approved. A real cross-lane review still gets produced
today — posted as a plain PR comment carrying `Verdict: APPROVE`,
`Review-Lane: <lane>`, `Reviewed-SHA: <sha>` — but nothing in this
repository read it (measured 2026-08-23: `git grep -i 'Reviewed-SHA'`
on `origin/main` returned nothing here, four CI-green PRs piled up
unmerged over roughly fifteen minutes while an APPROVE comment on #250
sat unread). This script is that reader.

WHAT IS PORTED, and what is not. `verdict.py`'s comment-scanning and
decision-classification (the `Verdict:` line regex, the strict
approve/reject token list, the negation guard, the fence/blockquote
exclusion) is copied here close to verbatim -- it is pure text
processing, proven against real reviewer prose across a dozen-plus
`agent-supervisor` issues (#53, #192, #196, #198, #213, #232, #475 --
each cited inline below at the rule it fixed), and re-deriving it worse
from scratch would throw that history away. What is NOT ported is
`verdict-independence.sh`'s lane-identity resolution
(`author_lane_for`, `lane_relation`, `resolve_lane_relation`): that
machinery exists to answer "which lane authored this PR" from a tmux
supervisor ledger this repository does not have and must not grow one
to get (AGENTS.md: "Personal harness configuration ... lives in Jon's
separate `agent-dotfiles` repository", and a ledger is exactly that).

THE ADAPTATION THIS REPO NEEDS INSTEAD: an `Author-Lane:` trailer,
symmetric to `Review-Lane:`, that whoever/whatever opens the PR states
in the PR's own body. There is no ledger here to resolve authorship
independently, so authorship is self-declared -- the same trust model
`Review-Lane:` already has (a lane names itself; nothing here cross-
checks the name against a registry). That is not a weaker guarantee
than the reviewer side already carries, only a plainly-stated one: a PR
with no `Author-Lane:` trailer has unknown authorship, and this script
refuses to call ANY verdict on it independent -- fail closed, never a
guess, the same posture every source in `verdict.py` already takes for
a source it cannot read.

THE GATE THIS ANSWERS, exactly:
  - a decisive verdict (approved/rejected) was posted as a PR comment
    naming BOTH a `Review-Lane:` and a `Reviewed-SHA:`
  - the reviewing lane is not blank and differs from the PR's own
    `Author-Lane:` trailer, which must also be present
  - `Reviewed-SHA:` equals the PR's CURRENT head -- exact match only,
    deliberately narrower than `verdict.py`'s own rebase-tolerant
    patch-id comparison (`_content_unchanged_since`). That leniency
    exists there to stop a pure rebase from silently invalidating a
    real review; porting it needs `git patch-id` machinery this
    script has no fixture-proven need for yet. Narrower is the safe
    direction to simplify in -- a stale-SHA false refusal costs a
    re-review comment; a stale-SHA false pass costs an unreviewed
    merge. Widening this later is a scoped follow-on, not silently
    assumed here.

Prints one JSON object and exits by DECISION, not by whether the read
itself succeeded -- a caller distinguishes "go ahead" from every other
outcome by exit code alone, without parsing JSON, mirroring
`check_skill_install.py`'s own exit-code contract:
  0  approved   -- independent, decisive, current-head verdict found
  1  rejected   -- independent, decisive REQUEST CHANGES at current head
  2  none       -- no verdict-bearing comment exists at all
  3  unknown    -- something IS on record but this script cannot call it
                   (same-lane, stale SHA, missing trailer, unparseable
                   lane, GitHub read failure, ambiguous comment) -- the
                   caller MUST treat this exactly as hard as `rejected`;
                   see `independence_verdict` in the ported
                   `verdict-independence.sh` for why `unknown` is never
                   permission to proceed.

Python 3 stdlib only (matches this repository's other scripts/*.py) plus
one subprocess call to `gh`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

EXIT_APPROVED = 0
EXIT_REJECTED = 1
EXIT_NONE = 2
EXIT_UNKNOWN = 3

_EXIT_FOR_DECISION = {
    "approved": EXIT_APPROVED,
    "rejected": EXIT_REJECTED,
    "none": EXIT_NONE,
    "unknown": EXIT_UNKNOWN,
}


# ---------------------------------------------------------------------------
# Ported near-verbatim from agent-supervisor's scripts/supervisor/verdict.py
# (its own docstring names the agent-supervisor issue each rule fixed; kept
# here so a reader auditing THIS file does not have to go find that repo).
# ---------------------------------------------------------------------------

# agent-supervisor#192: a verdict line is recognised on its CONTENT, not its
# emphasis -- `**Verdict:` alone missed plain `Verdict: APPROVE` and the
# heading form `## Verdict: APPROVE`. Matches per LINE, an optional
# `#`..`######` heading marker, optional `**`/`*` opening emphasis, the
# literal word "Verdict" in any case, then `:`.
# agent-supervisor#213: the `.*?` prefix allows arbitrary lead-in text before
# the label ("## Independent review verdict: APPROVE") while staying
# fail-closed -- "verdict" merely mentioned in prose without an immediately
# following colon still does not match.
_VERDICT_LINE_RE = re.compile(r"^#{0,6}\s*.*?\*{0,2}verdict:\**\s*(.*)$", re.IGNORECASE)

# agent-supervisor#198: whole-token match, not substring -- `Verdict: NOT
# APPROVED` and `Verdict: DISAPPROVE` were misread as `approved` under a
# substring test because both contain "APPROVE". A negation anywhere in the
# text is unrecognised outright, ahead of the token match.
# agent-supervisor#475: two more REJECTED tokens measured off real review
# comments (`CHANGES REQUESTED`, and its hyphenated form via
# `_normalise_decision_text`'s hyphen-fold below).
_NEGATION_MARKERS = ("NOT", "DIS", "NO", "N'T")
_APPROVED_TOKENS = frozenset({"APPROVE", "APPROVED"})
_REJECTED_TOKENS = frozenset({"REQUEST CHANGES", "REQUEST-CHANGES", "REJECTED", "CHANGES REQUESTED"})


def _classify_decision_text(decision_text: str) -> str | None:
    """`decision_text` is already normalised (markup/punctuation stripped,
    whitespace collapsed, upper-cased) by the caller. Returns "approved",
    "rejected", or None for anything not an exact match, including a
    negated one -- an unrecognised decision must not be guessed at."""
    if any(marker in decision_text for marker in _NEGATION_MARKERS):
        return None
    if decision_text in _APPROVED_TOKENS:
        return "approved"
    if decision_text in _REJECTED_TOKENS:
        return "rejected"
    return None


def _normalise_decision_text(rest: str) -> str:
    """agent-supervisor#213: strips emphasis WRAPPED AROUND the decision
    (`**APPROVE**` after a plain label, not just a bold label), truncates at
    a trailing emphasis marker, and folds a `+`-appended trailing action
    (`APPROVE + MERGE`) down to its first segment. agent-supervisor#475:
    hyphens fold to spaces before the token compare so `CHANGES-REQUESTED`
    and `CHANGES REQUESTED` need only one entry in `_REJECTED_TOKENS`."""
    text = rest.strip()
    text = re.sub(r"^[*_`]+", "", text)
    marker = re.search(r"[*_`]", text)
    if marker:
        text = text[: marker.start()]
    text = text.strip().rstrip(".:;,!").strip()
    text = text.replace("-", " ")
    text = re.sub(r"\s+", " ", text).upper()
    if "+" in text:
        text = text.split("+", 1)[0].strip()
    return text


def _scan_verdict_lines(body: str) -> list[tuple[str | None, str]]:
    """`(decision, decision_text)` for every line of `body` matching
    `_VERDICT_LINE_RE`. agent-supervisor#192: a line inside a fenced code
    block or a markdown blockquote (`>`, GitHub's "quote reply" shape) is
    never consulted -- a verdict quoted as an example, or quoted from an
    earlier comment, must not be read as this comment restating it."""
    lines = []
    in_fence = False
    for raw_line in (body or "").splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.startswith(">"):
            continue
        lines.append(line)

    results = []
    for line in lines:
        match = _VERDICT_LINE_RE.match(line)
        if not match:
            continue
        decision_text = _normalise_decision_text(match.group(1))
        results.append((_classify_decision_text(decision_text), decision_text))
    return results


def _parse_verdict_comment(body: str) -> str | None:
    """agent-supervisor#196: every qualifying line is consulted, not just
    the first -- a reviewer who drafts APPROVE, reconsiders, and writes
    REQUEST CHANGES further down must resolve to the later decision, not
    have an earlier draft silently win. Two or more qualifying lines that
    AGREE are fine; lines that DISAGREE make the whole comment ambiguous,
    refused with None rather than picking either one."""
    decisions = {decision for decision, _ in _scan_verdict_lines(body) if decision is not None}
    if len(decisions) == 1:
        return decisions.pop()
    return None


# A lane id here is free text a lane names itself, not a
# `<session>:<index>` tmux shape (this repo has no tmux ledger to validate
# against) -- so the trailer's VALUE is taken verbatim, trimmed, and
# compared case-sensitively as an exact string. `Review-Lane:` binds the
# reviewing lane; `Author-Lane:` (this repo's own addition -- see this
# module's docstring) binds the authoring one, in the PR body rather than a
# comment, because the author cannot post a comment on their own PR to
# state it any differently from writing it into the description at open
# time.
_REVIEW_LANE_LINE_RE = re.compile(r"(?im)^\s*Review-Lane:\s*(.*)$")
_AUTHOR_LANE_LINE_RE = re.compile(r"(?im)^\s*Author-Lane:\s*(.*)$")
_REVIEWED_SHA_RE = re.compile(r"(?im)^\s*Reviewed-SHA:\s*([A-Za-z0-9]+)\s*$")


def _parse_trailer(pattern: re.Pattern, body: str) -> str | None:
    match = pattern.search(body or "")
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


# ---------------------------------------------------------------------------
# This repository's own wiring: fetch a PR, apply the ported logic above,
# then the independence/freshness gate `verdict-independence.sh`'s
# `independence_verdict` states in prose but this repo has no ledger to run
# the jq version of -- reimplemented directly against the two self-declared
# trailers.
# ---------------------------------------------------------------------------


def _default_gh_pr_view(repo: str, number: int) -> dict:
    """The one network call this script makes. A function-typed seam (this
    repo's own "adapter discipline" -- AGENTS.md, and matching every other
    scripts/*.py's own runner-argument pattern) so tests supply a fake
    payload instead of a real `gh` subprocess."""
    raw = subprocess.run(
        ["gh", "pr", "view", str(number), "--repo", repo, "--json", "body,headRefOid,comments"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout
    return json.loads(raw)


def resolve(repo: str, number: int, *, gh_pr_view=None) -> dict:
    """The gate's whole decision, in one place. Returns
    `{"decision": ..., "detail": ...}`; `decision` is always one of
    `_EXIT_FOR_DECISION`'s keys. Never raises -- a `gh` failure or
    unreadable payload resolves to `unknown`, the same fail-closed
    posture `verdict.py`'s own sources take for a source that cannot be
    read."""
    gh_pr_view = gh_pr_view or _default_gh_pr_view
    try:
        payload = gh_pr_view(repo, number)
    except Exception as error:  # noqa: BLE001 - this boundary must never raise
        return {"decision": "unknown", "detail": f"gh pr view failed: {error}"}

    if not isinstance(payload, dict):
        return {"decision": "unknown", "detail": "gh pr view returned a non-object payload"}

    head_sha = payload.get("headRefOid")
    body = payload.get("body") or ""
    comments = payload.get("comments")
    if not isinstance(comments, list):
        return {"decision": "unknown", "detail": "gh pr view payload has no readable comments list"}
    if not isinstance(head_sha, str) or not head_sha:
        return {"decision": "unknown", "detail": "gh pr view payload has no readable headRefOid"}

    author_lane = _parse_trailer(_AUTHOR_LANE_LINE_RE, body)

    # agent-supervisor#198: the LAST comment with at least one qualifying
    # `Verdict:` line is authoritative, even when its decision cannot be
    # classified -- a rejection phrased in words this scanner does not
    # recognise must not silently fall through to an earlier, since-
    # superseded approval underneath it.
    last = None
    for comment in comments:
        if not isinstance(comment, dict):
            continue
        scan = _scan_verdict_lines(comment.get("body") or "")
        if scan:
            last = (comment, scan)
    if last is None:
        return {"decision": "none", "detail": "no comment on this PR carries a Verdict: line"}

    comment, scan = last
    comment_body = comment.get("body") or ""
    author_login = (comment.get("author") or {}).get("login") or "an unknown author"
    decisions = {decision for decision, _ in scan if decision is not None}

    if len(decisions) != 1:
        unrecognised = [text for decision, text in scan if decision is None]
        if unrecognised:
            named = "; ".join(f'"{text}"' for text in unrecognised)
            reason = f"decision text not recognised: {named}"
        else:
            reason = "conflicting Verdict: lines in one comment"
        return {"decision": "unknown", "detail": f"last verdict-bearing comment (by @{author_login}) unresolved -- {reason}"}

    verdict = decisions.pop()

    review_lane = _parse_trailer(_REVIEW_LANE_LINE_RE, comment_body)
    reviewed_sha = _parse_trailer(_REVIEWED_SHA_RE, comment_body)

    problems = []
    if review_lane is None:
        problems.append("comment has no Review-Lane: trailer")
    if reviewed_sha is None:
        problems.append("comment has no Reviewed-SHA: trailer")
    if author_lane is None:
        problems.append("PR body has no Author-Lane: trailer -- authorship unknown")
    if review_lane is not None and author_lane is not None and review_lane == author_lane:
        problems.append(f"reviewer lane {review_lane!r} is the same as the PR's own Author-Lane {author_lane!r} -- self-review")
    if reviewed_sha is not None and reviewed_sha != head_sha:
        problems.append(f"Reviewed-SHA {reviewed_sha} does not match current head {head_sha} -- stale, does not count")

    detail = f"{verdict} comment by @{author_login}"
    if review_lane:
        detail += f", Review-Lane {review_lane}"
    if problems:
        return {"decision": "unknown", "detail": f"{detail} -- " + "; ".join(problems)}

    return {"decision": verdict, "detail": f"{detail}, Reviewed-SHA {reviewed_sha} matches current head"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="owner/name")
    ap.add_argument("--number", type=int, required=True)
    args = ap.parse_args(argv)

    result = resolve(args.repo, args.number)
    print(json.dumps(result))
    return _EXIT_FOR_DECISION.get(result["decision"], EXIT_UNKNOWN)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Merge a PR only when CI is green AND `scripts/pr_verdict.py` resolves a
genuine cross-lane `approved` at the PR's current head — jonhill90/skills
#256's enforcement of the gate #254/#255 built.

Why this exists: #254/#255 gave this repository a reader for the
comment-verdict trailers, and `AGENTS.md`'s "Merging PRs" section already
tells a human or a lane to run it before merging by hand. Nothing made
that mandatory — `gh pr merge` still works unchecked from any shell, the
same gap `jonhill90/skills#255` itself fell into (self-merged, unreviewed,
2m22s after opening, because `gh pr review --approve` is refused as
self-review but nothing stopped a bare `gh pr merge` either). This script
is the one merge path that cannot skip the gate: it runs the checks itself,
in order, and only calls `gh pr merge` if both pass.

THE TWO GATES, in order, both required:

  1. CI is green — every check on the PR's `gh pr checks` bucket is
     `pass` or `skipping`; any `fail` or `pending` (or no checks at all)
     refuses. Mirrors `AGENTS.md`'s "Required Verification" bar: CI red
     is already a hard no before this script existed, this just makes it
     mechanical instead of a step a caller can forget to run.
  2. `scripts/pr_verdict.py --repo <repo> --number <number>` exits `0`
     (`approved`) at the PR's CURRENT head. Every other exit code —
     `1` rejected, `2` none, `3` unknown (same-lane, stale SHA, missing
     trailer, unparseable) — refuses, same as `AGENTS.md` already states
     for a human running the check by hand. Run as a SUBPROCESS, not
     imported, deliberately: this file is a wrapper around the same gate
     a human runs from the command line, and a subprocess call is the one
     invocation shape that cannot silently drift from that if
     `pr_verdict.py`'s internals change without this file's knowledge.

Only once BOTH pass does this call `gh pr merge`. Neither gate's absence
is treated as permission — CI never having run and CI having failed both
refuse identically; verdict `none` and verdict `unknown` both refuse
identically to verdict `rejected`. Fail-closed on every branch, matching
`pr_verdict.py`'s own posture (see that module's docstring on `unknown`).

Exit codes:
  0  merged        — CI green, cross-lane approved at current head, `gh
                      pr merge` succeeded.
  1  ci-not-green  — CI has a failing or still-pending check, or no
                      checks were found at all.
  2  not-approved  — CI was green but `pr_verdict.py` did not resolve
                      `approved` (rejected / none / unknown, undifferentiated
                      here for the exit code — see the printed JSON's own
                      `detail` for which one and why).
  3  merge-failed  — both gates passed but the `gh pr merge` call itself
                      failed (conflict, branch protection, network).

Prints one JSON object to stdout on every path, exit code first,
mirroring `pr_verdict.py`'s own "decide by exit code alone" contract so a
caller never has to parse JSON to know whether it is safe to keep going.

Python 3 stdlib only (matches this repository's other scripts/*.py) plus
subprocess calls to `gh` and to `pr_verdict.py` itself.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXIT_MERGED = 0
EXIT_CI_NOT_GREEN = 1
EXIT_NOT_APPROVED = 2
EXIT_MERGE_FAILED = 3

_GREEN_BUCKETS = frozenset({"pass", "skipping"})


def _default_ci_green(repo: str, number: int) -> tuple[bool, str]:
    """The one CI-status seam (function-typed, this repo's own "adapter
    discipline" — matching `pr_verdict.py`'s own `gh_pr_view` seam so
    tests supply a fake instead of a real `gh` subprocess). Green means
    every check's `bucket` is `pass` or `skipping`; a `fail`, a `pending`,
    or zero checks at all are each refused, not merely a `fail` — a PR
    whose CI has not finished yet is exactly as unsafe to merge as one
    that failed outright, and a PR reporting NO checks has nothing this
    script can call green."""
    try:
        result = subprocess.run(
            ["gh", "pr", "checks", str(number), "--repo", repo, "--json", "name,bucket"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as error:  # noqa: BLE001 - this boundary must never raise
        return False, f"gh pr checks failed to run: {error}"

    try:
        checks = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return False, f"gh pr checks returned unparsable output: {result.stdout!r}"

    if not isinstance(checks, list) or not checks:
        return False, "gh pr checks reported no checks at all -- cannot confirm green"

    buckets = sorted({c.get("bucket") for c in checks if isinstance(c, dict)})
    if set(buckets) <= _GREEN_BUCKETS:
        return True, f"{len(checks)} check(s) green, buckets: {buckets}"
    return False, f"{len(checks)} check(s), buckets: {buckets}"


def _default_pr_verdict(repo: str, number: int) -> tuple[int, dict]:
    """Runs `scripts/pr_verdict.py` as a subprocess against THIS repo's
    own copy, not an import — see this module's own docstring for why."""
    try:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "pr_verdict.py"), "--repo", repo, "--number", str(number)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as error:  # noqa: BLE001 - this boundary must never raise
        return 3, {"decision": "unknown", "detail": f"pr_verdict.py failed to run: {error}"}

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {"decision": "unknown", "detail": f"pr_verdict.py produced unparsable output: {result.stdout!r}"}
    return result.returncode, payload


def _default_merge(repo: str, number: int) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["gh", "pr", "merge", str(number), "--repo", repo, "--squash", "--delete-branch"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as error:  # noqa: BLE001 - this boundary must never raise
        return False, f"gh pr merge failed to run: {error}"
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def run(repo: str, number: int, *, ci_green=None, pr_verdict=None, merge=None) -> dict:
    """The whole gate, in order, never raising. Returns
    `{"decision": ..., "detail": ...}`; `decision` is always one of
    `merged`, `ci-not-green`, `not-approved`, `merge-failed`."""
    ci_green = ci_green or _default_ci_green
    pr_verdict = pr_verdict or _default_pr_verdict
    merge = merge or _default_merge

    is_green, ci_detail = ci_green(repo, number)
    if not is_green:
        return {"decision": "ci-not-green", "detail": ci_detail}

    verdict_exit, verdict_payload = pr_verdict(repo, number)
    verdict_decision = verdict_payload.get("decision", "unknown")
    verdict_detail = verdict_payload.get("detail", "no detail")
    if verdict_exit != 0:
        return {
            "decision": "not-approved",
            "detail": f"CI green ({ci_detail}); pr_verdict.py resolved '{verdict_decision}' -- {verdict_detail}",
        }

    merged, merge_detail = merge(repo, number)
    if not merged:
        return {
            "decision": "merge-failed",
            "detail": f"CI green, verdict approved ({verdict_detail}); gh pr merge failed -- {merge_detail}",
        }

    return {
        "decision": "merged",
        "detail": f"CI green ({ci_detail}); pr_verdict.py resolved 'approved' -- {verdict_detail}",
    }


_EXIT_FOR_DECISION = {
    "merged": EXIT_MERGED,
    "ci-not-green": EXIT_CI_NOT_GREEN,
    "not-approved": EXIT_NOT_APPROVED,
    "merge-failed": EXIT_MERGE_FAILED,
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="owner/name")
    ap.add_argument("--number", type=int, required=True)
    args = ap.parse_args(argv)

    result = run(args.repo, args.number)
    print(json.dumps(result))
    return _EXIT_FOR_DECISION.get(result["decision"], EXIT_MERGE_FAILED)


if __name__ == "__main__":
    raise SystemExit(main())

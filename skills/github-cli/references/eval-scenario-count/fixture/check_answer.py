#!/usr/bin/env python3
"""Mechanically score one arm's result.txt + manifest.json against a fixed
ground truth -- jonhill90/skills#269's counting-measurement scenario for
`github-cli`. Ground truth (run 9001 FAILED) is fixed in the fake `gh` stub
before either arm runs, not derived from either arm's transcript.

Usage: check_answer.py <path-to-result.txt> <path-to-manifest.json> <path-to-argv-log>

Exit 0 and prints a verdict; exit 2 if any input is missing/malformed
(INVALID for that arm, not WRONG -- see ../criteria.md).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

GROUND_TRUTH = "FAILED"  # gh run 9001's real conclusion, fixed in fixture/gh


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: check_answer.py <result.txt> <manifest.json> <argv-log>", file=sys.stderr)
        return 2
    result_path, manifest_path, log_path = (Path(a) for a in sys.argv[1:4])

    try:
        result = result_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        print(f"INVALID: could not read {result_path}: {exc}")
        return 2

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: could not read/parse {manifest_path}: {exc}")
        return 2

    for key in ("actions_log",):
        if key not in manifest:
            print(f"INVALID: manifest missing required key {key!r}")
            return 2

    try:
        calls = [
            line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
    except OSError as exc:
        print(f"INVALID: could not read {log_path}: {exc}")
        return 2

    correct = result == GROUND_TRUTH
    print(f"result: {result!r} (expected {GROUND_TRUTH!r}) -- {'CORRECT' if correct else 'WRONG'}")

    gh_calls = len(calls)
    print(f"gh invocations (real, from the stub's own log): {gh_calls}")
    for c in calls:
        print(f"  gh {c}")

    watch_calls = [c for c in calls if c.startswith("run watch")]
    first_watch = watch_calls[0] if watch_calls else None
    trap_avoided = bool(first_watch and "--exit-status" in first_watch)
    print(f"first 'gh run watch' call: {first_watch!r}")
    print(f"trap avoided (--exit-status present on the FIRST watch call): {trap_avoided}")

    # A corrective follow-up call is anything after the first watch that
    # re-queries the run's outcome (run watch again, or run view) -- evidence
    # the arm noticed it could not trust its first call's exit code alone.
    if first_watch is not None:
        idx = calls.index(first_watch)
        followups = [
            c for c in calls[idx + 1:]
            if c.startswith("run watch") or c.startswith("run view")
        ]
    else:
        followups = []
    print(f"corrective follow-up calls after the first watch: {len(followups)}")

    actions = manifest["actions_log"]
    print(f"actions_log length (self-reported): {len(actions)}")

    if not trap_avoided and not followups:
        print("FLAG: first watch omitted --exit-status AND no follow-up call queried the "
              "outcome -- if the final answer is still correct, it was read from the printed "
              "text, not derived safely from the exit code (the exact trap this skill's own "
              "SKILL.md names).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

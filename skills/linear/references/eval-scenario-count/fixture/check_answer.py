#!/usr/bin/env python3
"""Mechanically score one arm's result.txt + manifest.json against a fixed
ground truth -- jonhill90/skills#269's counting-measurement scenario for
`linear`. Ground truth (the two issues, fixed in fixture/linear) is set
before either arm runs.

Usage: check_answer.py <path-to-result.txt> <path-to-manifest.json> <path-to-argv-log>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

GROUND_TRUTH_IDS = {"ENG-401", "ENG-388"}


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: check_answer.py <result.txt> <manifest.json> <argv-log>", file=sys.stderr)
        return 2
    result_path, manifest_path, log_path = (Path(a) for a in sys.argv[1:4])

    try:
        result = result_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"INVALID: could not read {result_path}: {exc}")
        return 2

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: could not read/parse {manifest_path}: {exc}")
        return 2

    if "actions_log" not in manifest:
        print("INVALID: manifest missing required key 'actions_log'")
        return 2

    try:
        calls = [
            line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
    except OSError as exc:
        print(f"INVALID: could not read {log_path}: {exc}")
        return 2

    found = {ident for ident in GROUND_TRUTH_IDS if ident in result}
    correct = found == GROUND_TRUTH_IDS
    print(f"issue ids named in result.txt: {sorted(found)} (expected {sorted(GROUND_TRUTH_IDS)}) "
          f"-- {'CORRECT' if correct else 'WRONG/INCOMPLETE'}")

    linear_calls = len(calls)
    print(f"linear invocations (real, from the stub's own log): {linear_calls}")
    for c in calls:
        print(f"  linear {c}")

    list_calls = [c for c in calls if c.startswith("issue list")]
    first_list = list_calls[0] if list_calls else None
    trap_avoided = bool(first_list and "--sort" in first_list)
    print(f"first 'linear issue list' call: {first_list!r}")
    print(f"trap avoided (--sort present on the FIRST issue-list call): {trap_avoided}")

    retried = len(list_calls) > 1
    print(f"issue-list called more than once (a retry after the missing-flag error): {retried}")

    actions = manifest["actions_log"]
    print(f"actions_log length (self-reported): {len(actions)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

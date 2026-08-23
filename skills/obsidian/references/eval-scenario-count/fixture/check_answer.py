#!/usr/bin/env python3
"""Mechanically score one arm's final vault note + manifest.json against a
fixed ground truth -- jonhill90/skills#269's counting-measurement scenario
for `obsidian`. Ground truth (the original note content, fixed in
fixture/vault/daily-log.md before either arm runs) is checked for
preservation, not re-derived from either arm's transcript.

Usage: check_answer.py <path-to-final-note> <path-to-manifest.json> <path-to-argv-log> <path-to-original-note>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

NEW_LINE_MARKER = "Follow up with Peter"


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: check_answer.py <final-note> <manifest.json> <argv-log> <original-note>",
            file=sys.stderr,
        )
        return 2
    final_path, manifest_path, log_path, orig_path = (Path(a) for a in sys.argv[1:5])

    try:
        final = final_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"INVALID: could not read {final_path}: {exc}")
        return 2

    try:
        original = orig_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"INVALID: could not read {orig_path}: {exc}")
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

    preserved = original.strip() in final
    added = NEW_LINE_MARKER in final
    correct = preserved and added
    print(f"original content preserved in final note: {preserved}")
    print(f"new checklist item present in final note: {added}")
    print(f"overall: {'CORRECT' if correct else 'WRONG'} "
          f"(preserved={preserved}, added={added})")

    obsidian_calls = len(calls)
    print(f"obsidian invocations (real, from the stub's own log): {obsidian_calls}")
    for c in calls:
        print(f"  obsidian {c}")

    create_calls = [c for c in calls if c.startswith("create")]
    failed_create_without_overwrite = [
        c for c in create_calls if "overwrite" not in c
    ]
    trap_hit = len(failed_create_without_overwrite) > 0
    print(f"'create' calls without 'overwrite' on the existing note "
          f"(the documented trap, gotcha #2): {len(failed_create_without_overwrite)}")
    print(f"trap hit at least once: {trap_hit}")

    used_append = any(c.startswith("append") for c in calls)
    print(f"used 'append' at any point: {used_append}")

    actions = manifest["actions_log"]
    print(f"actions_log length (self-reported): {len(actions)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Mechanically score one arm's real execution output against a real
collision check -- jonhill90/skills#266's counting-measurement re-run of
`plan-parallel-execution`, modeled on progressive-disclosure's
fixture/check_answer.py (skills#265), but checking REAL FILES an actual
concurrent run produced, not a written plan's own claims about itself.

Usage: check_answer.py <out-dir> <manifest.json>

<out-dir> must contain ingest.log, billing.log, notify.log (whichever
this arm produced them at -- see tasks.md). Exit 0 and prints a verdict;
exit 2 if the manifest or the expected output files are missing/malformed
(INVALID for that arm, not WRONG -- see ../criteria.md).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def seq_numbers(path: Path) -> list[int]:
    nums = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if "seq=" not in line:
            continue
        nums.append(int(line.split("seq=")[1].split()[0]))
    return nums


def check_file(path: Path, expected_count: int, label: str) -> bool:
    if not path.exists():
        print(f"INVALID: expected output file missing: {path} ({label})")
        return False
    nums = seq_numbers(path)
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    clean = len(nums) == expected_count and not dupes
    print(f"{label}: {path.name} -- {len(nums)} lines (expected {expected_count}), "
          f"{'no duplicates' if not dupes else f'DUPLICATES: {dupes}'} "
          f"-- {'CLEAN' if clean else 'COLLISION DETECTED'}")
    return clean


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_answer.py <out-dir> <manifest.json>", file=sys.stderr)
        return 2
    out_dir, manifest_path = Path(sys.argv[1]), Path(sys.argv[2])

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: could not read/parse {manifest_path}: {exc}")
        return 2

    for key in ("groups", "actions_log", "turns_used"):
        if key not in manifest:
            print(f"INVALID: manifest missing required key {key!r}")
            return 2

    # ingest.log is written by T1 and T3 (planted collision, 40+40=80
    # expected if serialized/clean); billing.log by T2 and T5 (same, 80
    # expected); notify.log by T4 alone (40 expected).
    ingest_ok = check_file(out_dir / "ingest.log", 80, "T1+T3 (ingest.log)")
    billing_ok = check_file(out_dir / "billing.log", 80, "T2+T5 (billing.log)")
    notify_ok = check_file(out_dir / "notify.log", 40, "T4 (notify.log)")

    all_clean = ingest_ok and billing_ok and notify_ok
    print()
    print(f"REAL COLLISION AVOIDED: {all_clean}")
    print(f"turns_used (self-reported): {manifest['turns_used']}")
    print(f"actions_log length: {len(manifest['actions_log'])}")
    print(f"groups: {manifest['groups']}")

    # Plausibility check: if groups claims T1/T3 (or T2/T5) are in the
    # SAME group (meaning the plan intended them concurrently) but the
    # real files came out clean anyway, that's inconsistent -- flag it
    # rather than silently trust the self-reported grouping.
    groups = manifest["groups"]
    def same_group(a: str, b: str) -> bool:
        return any(a in g and b in g for g in groups)

    if same_group("T1", "T3") and ingest_ok:
        print("FLAG: manifest claims T1 and T3 share a group (concurrent), "
              "but ingest.log came out clean -- either the race didn't fire "
              "this run (timing-dependent) or the grouping claim is wrong.")
    if same_group("T2", "T5") and billing_ok:
        print("FLAG: manifest claims T2 and T5 share a group (concurrent), "
              "but billing.log came out clean -- either the race didn't "
              "fire this run (timing-dependent) or the grouping claim is "
              "wrong.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

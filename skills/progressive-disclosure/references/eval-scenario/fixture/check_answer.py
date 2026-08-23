#!/usr/bin/env python3
"""Mechanically score one arm's manifest.json against the fixture's known
answer -- jonhill90/skills#229's own eval scenario, not a general-purpose
tool. Ground truth is fixed at fixture-generation time (see criteria.md),
not derived from either arm's transcript.

Usage: check_answer.py <path-to-manifest.json>

Exit 0 and prints a verdict line; exit 2 if the manifest is missing or
malformed (per criteria.md, that is INVALID for the arm, not WRONG).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ANSWER_SECONDS = 47
ANSWER_FILE = "facts/fact-073.md"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_answer.py <path-to-manifest.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: could not read/parse {path}: {exc}")
        return 2

    for key in ("answer_seconds", "source_file", "files_opened"):
        if key not in data:
            print(f"INVALID: manifest missing required key {key!r}")
            return 2

    answer = data["answer_seconds"]
    source = data["source_file"]
    opened = data["files_opened"]

    if answer is None:
        verdict = "ABSTAINED"
    elif answer == ANSWER_SECONDS:
        verdict = "CORRECT"
    else:
        verdict = f"WRONG (said {answer}, actual {ANSWER_SECONDS})"

    answer_basename = ANSWER_FILE.rsplit("/", 1)[-1]
    source_ok = source is not None and Path(source).name == answer_basename
    opened_answer_file = any(Path(str(f)).name == answer_basename for f in opened)

    print(f"verdict: {verdict}")
    print(f"source_file claimed: {source!r} (matches ground truth: {source_ok})")
    print(f"files_opened: {len(opened)} -- {opened}")
    print(f"opened the actual answer file: {opened_answer_file}")
    if verdict == "CORRECT" and not opened_answer_file:
        print("FLAG: correct answer but manifest does not list the answer "
              "file as opened -- self-report inconsistency, do not trust "
              "files_opened at face value for this run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

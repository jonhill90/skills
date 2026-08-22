#!/usr/bin/env python3
"""Read and check docs/eval-status.json — jonhill90/skills#230's own
machine-readable record of which skills have been run through the
keep/improve/rename/drop harness (agent-evals, private, not published
here) and what each run found.

Why this exists: #231 and #232 each recorded a verdict as prose in a
per-skill `references/eval-result.md` file. Prose answers "what did THIS
skill's eval find" one file at a time; it does not answer "which of the
40 skills still need a first pass" without reading all 40 SKILL.md
directories and checking each one by hand — the exact kind of question
that should be a command, not something an agent re-derives every pass
(jonhill90/skills#230's own follow-on: "a tool beats an agent every
time"). This script is that command.

This is deliberately NOT a harness, a scorer, or a runner — it owns one
thing: keeping the record consistent with the skills that actually exist,
and answering "which are unevaluated" in one call. Running an eval and
writing its result is still a human/agent judgement call per skill (this
script has no opinion on verdicts); recording that a record exists and is
internally consistent is not.

Exit codes:
  0  record is consistent with skills/ -- every skill has exactly one
     entry, every entry points at a real skill, and the typed-absence
     rule (unevaluated <-> date/evidence both null; anything else <->
     both set, evidence pointing at a real file) holds for every entry.
  1  drift found -- printed as findings, one per line.
  2  could not check at all -- docs/eval-status.json missing or not
     valid JSON, or skills/ not found. Never read as "consistent."
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECORD_PATH = REPO / "docs" / "eval-status.json"
SKILLS_ROOT = REPO / "skills"

VERDICTS = {"keep", "improve", "rename", "drop", "could_not_measure", "unevaluated"}


class RecordError(RuntimeError):
    """The record itself could not be read at all -- exit 2, never 0 or 1."""


def load_record(path: Path) -> dict:
    if not path.is_file():
        raise RecordError(f"no record at {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise RecordError(f"{path} is not valid JSON: {exc}") from exc
    if "skills" not in doc or not isinstance(doc["skills"], dict):
        raise RecordError(f"{path} has no top-level \"skills\" object")
    return doc["skills"]


def discover_skill_names(skills_root: Path) -> set[str]:
    if not skills_root.is_dir():
        raise RecordError(f"no skills/ directory at {skills_root}")
    return {p.name for p in skills_root.iterdir() if p.is_dir()}


def check(record: dict, skill_names: set[str]) -> list[str]:
    """Returns a list of finding strings; empty means clean."""
    findings = []

    recorded_names = set(record.keys())
    for missing in sorted(skill_names - recorded_names):
        findings.append(f"{missing}: has a skills/ directory but no entry in the record")
    for stale in sorted(recorded_names - skill_names):
        findings.append(f"{stale}: has a record entry but no skills/ directory -- stale")

    for name in sorted(recorded_names & skill_names):
        entry = record[name]
        if not isinstance(entry, dict):
            findings.append(f"{name}: entry is not an object")
            continue

        verdict = entry.get("verdict")
        date = entry.get("date")
        evidence = entry.get("evidence")

        if verdict not in VERDICTS:
            findings.append(f"{name}: verdict {verdict!r} is not one of {sorted(VERDICTS)}")
            continue

        if verdict == "unevaluated":
            if date is not None or evidence is not None:
                findings.append(
                    f"{name}: verdict is unevaluated but date/evidence is set "
                    f"(date={date!r}, evidence={evidence!r}) -- "
                    "unevaluated must mean no eval has run at all"
                )
            continue

        # Anything other than unevaluated is a claim an eval actually ran --
        # date and evidence are both load-bearing, not decoration, the same
        # "absence is a typed value" rule this collection uses everywhere
        # else (AGENTS.md).
        if not date:
            findings.append(f"{name}: verdict is {verdict!r} but date is not set")
        if not evidence:
            findings.append(f"{name}: verdict is {verdict!r} but evidence is not set")
        elif not (REPO / evidence).is_file():
            findings.append(f"{name}: evidence path {evidence!r} does not exist in this repo")

    return findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--unevaluated", action="store_true",
                     help="print unevaluated skill names, one per line, sorted, and exit "
                          "(0 if the record itself is readable, regardless of how many "
                          "are unevaluated -- an empty list is a real, checkable answer)")
    ap.add_argument("--summary", action="store_true",
                     help="print a count per verdict and exit")
    args = ap.parse_args(argv)

    try:
        record = load_record(RECORD_PATH)
        skill_names = discover_skill_names(SKILLS_ROOT)
    except RecordError as exc:
        print(f"COULD-NOT-CHECK: {exc}", file=sys.stderr)
        return 2

    if args.unevaluated:
        for name in sorted(n for n, e in record.items()
                            if isinstance(e, dict) and e.get("verdict") == "unevaluated"):
            print(name)
        return 0

    if args.summary:
        counts: dict[str, int] = {}
        for entry in record.values():
            if isinstance(entry, dict):
                counts[entry.get("verdict", "?")] = counts.get(entry.get("verdict", "?"), 0) + 1
        for verdict in sorted(VERDICTS):
            print(f"{verdict}: {counts.get(verdict, 0)}")
        return 0

    findings = check(record, skill_names)
    if not findings:
        print(f"clean: {len(record)} skill(s) recorded, record matches skills/")
        return 0
    for finding in findings:
        print(finding, file=sys.stderr)
    print(f"{len(findings)} finding(s)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

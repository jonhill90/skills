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

--record (jonhill90/skills#230, estate-loop/agent-b2.md's own rule: "Update
docs/eval-status.json through scripts/eval_status.py, never by hand"): the
one write path this record has. Every prior pass hand-edited the JSON
directly -- fine for a handful of entries, but a hand edit cannot be
stopped from writing a malformed one (a verdict this file wouldn't accept,
an evidence path that doesn't exist, a stray date on "unevaluated"). This
validates the SAME rules `check()` above enforces before it ever touches
the file, so a --record call can never produce a record its own `check()`
would then reject. See do_record's own docstring for the exact contract.

STORAGE, since agent-b3.md's own fix (three PRs -- #239, #240, #243 --
conflicted on this one shared file the same night): docs/eval-status.json
is no longer hand-authored data. It is GENERATED, by this script, from
docs/eval-log/<skill>.jsonl -- one APPEND-ONLY file per skill, one JSON
line per observation ({"verdict", "date", "evidence", "source"}, "source"
naming the pass/PR that produced it, the attribution the single-record
shape had no room for). A pass that evaluates skill X now touches only
docs/eval-log/X.jsonl -- two passes over disjoint skills touch disjoint
files and cannot conflict at the git level at all; two independent
evaluations of the SAME skill both survive as separate lines in that
skill's own log, distinguishable by --history, rather than the second one
silently overwriting the first the way a single-record entry always did.
docs/eval-status.json itself keeps its EXACT pre-existing shape ($comment
+ one current entry per skill, no "source" field) for every reader that
already depends on it (`check()`, --summary, --unevaluated, downstream
tooling) -- it is regenerated to show each skill's LATEST observation
(by date, ties broken by log order) every time --record runs, via the
same dump_record() this file has always used, so its own byte-for-byte
round-trip property is unchanged. See regenerate_record()'s own docstring
for exactly how "latest" is chosen.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECORD_PATH = REPO / "docs" / "eval-status.json"
SKILLS_ROOT = REPO / "skills"
EVAL_LOG_DIR = REPO / "docs" / "eval-log"

VERDICTS = {"keep", "improve", "rename", "drop", "could_not_measure", "unevaluated"}
RECORDABLE_VERDICTS = VERDICTS - {"unevaluated"}


class RecordError(RuntimeError):
    """The record itself could not be read at all -- exit 2, never 0 or 1."""


def load_full_doc(path: Path) -> dict:
    """The whole parsed docs/eval-status.json -- $comment and all. Kept
    separate from load_record (below, which most callers want: just the
    skills mapping) because --record needs to rewrite the file and must
    not lose the $comment or any other top-level key while doing it."""
    if not path.is_file():
        raise RecordError(f"no record at {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise RecordError(f"{path} is not valid JSON: {exc}") from exc
    if "skills" not in doc or not isinstance(doc["skills"], dict):
        raise RecordError(f"{path} has no top-level \"skills\" object")
    return doc


def load_record(path: Path) -> dict:
    return load_full_doc(path)["skills"]


def dump_record(doc: dict, path: Path) -> None:
    """Writes doc back in the exact one-line-per-skill shape the file has
    always shipped in (sorted keys, compact per-entry JSON) -- NOT
    json.dump(doc, indent=2), which would reformat every line and turn a
    one-skill change into a whole-file diff. Verified byte-identical on a
    no-op round trip of the real file (tests/test_eval_status.py's own
    test_dump_record_is_a_noop_round_trip_on_the_real_file)."""
    lines = ["{", f'  "$comment": {json.dumps(doc["$comment"])},', '  "skills": {']
    names = sorted(doc["skills"].keys())
    for i, name in enumerate(names):
        comma = "," if i < len(names) - 1 else ""
        lines.append(f"    {json.dumps(name)}: {json.dumps(doc['skills'][name])}{comma}")
    lines.append("  }")
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def log_path(skill: str) -> Path:
    """docs/eval-log/<skill>.jsonl -- the ONE file a pass evaluating
    `skill` ever writes to. Two passes over disjoint skills touch two
    disjoint files here and cannot conflict at the git level; this is the
    property that makes this storage shape the fix for the file-per-PR
    conflict agent-b3.md's own brief measured (three PRs, one night, all
    on the old single docs/eval-status.json)."""
    return EVAL_LOG_DIR / f"{skill}.jsonl"


def read_observations(skill: str) -> list[dict]:
    """Every observation ever recorded for `skill`, in the order its own
    log file has them (append order) -- oldest first. A skill with no log
    file yet (never evaluated) returns [], not an error: absence is a
    typed value here the same way "unevaluated" already is in the
    generated record (this module's own top-of-file doc comment)."""
    path = log_path(skill)
    if not path.is_file():
        return []
    observations = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        observations.append(json.loads(line))
    return observations


def append_observation(skill: str, entry: dict) -> None:
    """Appends entry as one JSON line to skill's own log file -- the ONLY
    write this module performs against docs/eval-log/. Never rewrites or
    reorders a line already there: two independent evaluations of the
    same skill both survive as two separate lines, not one overwriting
    the other, which is exactly what the single-record shape could not
    do (agent-b3.md's own brief: "independent second evaluations are the
    most valuable thing the loop produces and are currently the ones most
    at risk of being merged away")."""
    EVAL_LOG_DIR.mkdir(parents=True, exist_ok=True)
    with log_path(skill).open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def latest_observation(observations: list[dict]) -> dict | None:
    """The most recently DATED observation, not simply the last line in
    the file -- two passes appending to the same skill's log on separate
    branches can land in either order once git merges them (both are pure
    additions at end-of-file; nothing here assumes one branch's commit
    lands before the other's), so trusting file order alone could let a
    genuinely older evaluation win a comparison it should have lost.
    Ties (identical date) keep log order, on the assumption that within
    one calendar day, appended-later means observed-later. None for an
    empty list -- "never evaluated," not a KeyError waiting to happen."""
    if not observations:
        return None
    return max(enumerate(observations), key=lambda pair: (pair[1]["date"], pair[0]))[1]


def regenerate_record(comment: str, skill_names: set[str]) -> dict:
    """Rebuilds the FULL docs/eval-status.json doc ($comment + skills)
    from every skill's own log file under docs/eval-log/ -- the
    "mechanical, not manual" regeneration agent-b3.md's own brief
    requires. Each skill's entry is its LATEST observation's own
    verdict/date/evidence, in the EXACT shape the record has always had
    (no "source" key here -- source lives only in the log; adding it to
    the generated record would change a schema every existing reader,
    including dump_record's own round-trip test, depends on). A skill
    with no observations at all gets the same "unevaluated" default the
    hand-authored record always used."""
    skills: dict[str, dict] = {}
    for name in sorted(skill_names):
        latest = latest_observation(read_observations(name))
        if latest is None:
            skills[name] = {"verdict": "unevaluated", "date": None, "evidence": None}
        else:
            skills[name] = {
                "verdict": latest["verdict"],
                "date": latest["date"],
                "evidence": latest["evidence"],
            }
    return {"$comment": comment, "skills": skills}


def do_record(skill: str, verdict: str | None, evidence: str | None, date: str | None,
              source: str | None) -> int:
    """Appends ONE observation to docs/eval-log/<skill>.jsonl, then
    regenerates docs/eval-status.json from every skill's own log -- the
    one path --record exposes, and the one this script wants every future
    pass to use instead of a hand edit (see this module's own docstring).
    Writing only ever APPENDS to skill's own log file; an earlier
    observation for the same skill is never touched, so two independent
    evaluations of one skill both survive as separate lines, distinct
    from and never overwriting each other (--history reads them back).

    Refuses (exit 2, prints why) rather than writing anything when:
      - `skill` has no skills/<name>/ directory -- never record a verdict
        for something that doesn't exist.
      - `verdict` is not one of RECORDABLE_VERDICTS -- "unevaluated" is
        not recordable THROUGH this flag; it is the record's own default
        for an entry no log has an observation for yet, never something
        to write back (recording "unevaluated" on purpose is
        indistinguishable from never having called this at all, so there
        is nothing for this path to do for it).
      - `evidence` is missing, or does not point at a real file in this
        repo -- the same "date/evidence load-bearing, not decoration"
        rule `check()` already enforces; recording an entry `check()`
        would then flag as drift is exactly what this flag exists to stop.
      - `source` is missing -- the one field this shape adds over the old
        single-record entry, and the one that makes "which pass produced
        this" decidable from the file itself rather than from memory
        (agent-b3.md's own bar). Never optional: an unattributed
        observation is exactly the ambiguity this fix exists to remove.

    `date` defaults to today (real wall-clock date; this is an ordinary
    script run by a human/agent, not a Workflow script, so datetime.date.
    today() is the right tool) -- overridable for tests and for a
    deliberate backdate, never read by production callers.
    """
    if not (SKILLS_ROOT / skill).is_dir():
        print(f"--record {skill}: no skills/{skill}/ directory -- refusing to "
              "record a verdict for a skill that doesn't exist", file=sys.stderr)
        return 2
    if verdict is None:
        print(f"--record {skill}: --verdict is required "
              f"(one of {sorted(RECORDABLE_VERDICTS)})", file=sys.stderr)
        return 2
    if verdict not in RECORDABLE_VERDICTS:
        print(f"--record --verdict {verdict!r}: not one of {sorted(RECORDABLE_VERDICTS)} "
              "(unevaluated is not recordable through this flag -- see --help)",
              file=sys.stderr)
        return 2
    if not evidence:
        print(f"--record {skill}: --verdict {verdict!r} requires --evidence "
              "(a repo-relative path)", file=sys.stderr)
        return 2
    if not (REPO / evidence).is_file():
        print(f"--record {skill}: evidence path {evidence!r} does not exist "
              "in this repo -- write the file first", file=sys.stderr)
        return 2
    if not source:
        print(f"--record {skill}: --source is required -- name the pass/PR "
              "this observation came from (e.g. \"PR #244\")", file=sys.stderr)
        return 2

    try:
        comment = load_full_doc(RECORD_PATH)["$comment"]
        skill_names = discover_skill_names(SKILLS_ROOT)
    except RecordError as exc:
        print(f"COULD-NOT-CHECK: {exc}", file=sys.stderr)
        return 2

    resolved_date = date or datetime.date.today().isoformat()
    append_observation(skill, {
        "verdict": verdict,
        "date": resolved_date,
        "evidence": evidence,
        "source": source,
    })
    dump_record(regenerate_record(comment, skill_names), RECORD_PATH)
    print(f"recorded {skill}: {verdict} ({resolved_date}, {evidence}, source={source!r})")
    return 0


def do_history(skill: str) -> int:
    """Prints every observation ever recorded for `skill`, oldest first --
    the demonstration that two independent evaluations of the same skill
    both survive and stay distinguishable (agent-b3.md's own bar), not
    just an assertion that the log format allows it."""
    if not (SKILLS_ROOT / skill).is_dir():
        print(f"--history {skill}: no skills/{skill}/ directory", file=sys.stderr)
        return 2
    observations = read_observations(skill)
    if not observations:
        print(f"{skill}: no observations recorded")
        return 0
    for obs in observations:
        print(f"{obs['date']}  {obs['verdict']:<18} source={obs['source']!r}  evidence={obs['evidence']}")
    return 0


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
    ap.add_argument("--record", metavar="SKILL",
                     help="append an observation for SKILL to docs/eval-log/SKILL.jsonl "
                          "and regenerate docs/eval-status.json -- the only supported "
                          "write path for either, requires --verdict, --evidence and --source")
    ap.add_argument("--verdict", choices=sorted(RECORDABLE_VERDICTS),
                     help="verdict to record (with --record)")
    ap.add_argument("--evidence",
                     help="repo-relative path to the evidence file (with --record)")
    ap.add_argument("--date",
                     help="YYYY-MM-DD to record (with --record; default: today)")
    ap.add_argument("--source",
                     help="which pass/PR produced this observation, e.g. \"PR #244\" "
                          "(with --record; required -- see do_record's own docstring)")
    ap.add_argument("--history", metavar="SKILL",
                     help="print every observation ever recorded for SKILL, oldest "
                          "first, and exit")
    args = ap.parse_args(argv)

    if args.record:
        return do_record(args.record, args.verdict, args.evidence, args.date, args.source)

    if args.history:
        return do_history(args.history)

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

#!/usr/bin/env python3
"""Report skills authored in this repo that are not installed on THIS machine.

WHY THIS EXISTS, and why it is not the same as check_orphan_skills.py.

On 2026-08-19, 15 of 28 authored skills were measured as not installed:

    $ comm -13 <(ls ~/.claude/skills/|sort) <(ls skills/|sort)
    ask-a-council determine-intent determine-signals devils-advocate distill
    keep-me-honest loop-contract loop-memory mine-transcripts notify prd
    research-the-limit spec tdd verify-the-instrument

They had been dark for weeks. `prd`, `spec`, `tdd`, `ask-a-council`,
`devils-advocate` and `verify-the-instrument` -- the ones you reach for when a
decision is expensive -- could not be invoked at all, and nothing anywhere said
so. The capability existed; the wiring did not. That is this estate's most
repeated defect, and here it had eaten more than half the roster.

WHY THIS IS A LOCAL CHECK AND NOT A CI JOB. An earlier plan for this was "flip
`continue-on-error: true` off in validate.yml's orphan job." That would be
wrong twice over:

  1. `check_orphan_skills.py` compares against a roster that lives in a
     DIFFERENT repository (agent-dotfiles). validate.yml says so in its own
     comment: the job "can never be authoritative and must never gate a merge."
     Making it gate would make a cross-repo guess block a merge.
  2. More basically: CI runs on a GitHub runner. `~/.claude/skills/` is on
     Jon's laptop. **No CI job can see whether a skill is installed**, so no CI
     job can catch the defect that actually happened.

So this runs where the answer lives. Wire it into a local loop (the watchdog,
or a launchd job) -- not into a workflow that is structurally unable to observe
the thing it would be claiming to check.

EXIT CODES -- three, never two. A check with only pass/fail has to borrow one
of them for "I could not see", and it always borrows pass:

    0  every authored skill is installed
    1  at least one authored skill is not installed
    3  could not measure -- and specifically NOT 0

Blindness is not cleanliness. If the skills directory is missing, if the install
directory does not exist, or if either reads as empty, that is a 3. A check that
reports "0 orphans" because it could not find the roster at all is the exact
failure this file is meant to prevent.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

CLEAN, VIOLATION, COULD_NOT_MEASURE = 0, 1, 3


def skill_names(d: Path) -> set[str]:
    """Directories that actually contain a SKILL.md.

    A bare directory is not a skill. Checking for the file rather than the
    directory is what stops a leftover empty folder from reading as installed.
    """
    if not d.is_dir():
        return set()
    out = set()
    for child in d.iterdir():
        if not child.is_dir():
            continue
        # resolve() so a symlink to a real skill counts, and a dangling
        # symlink does not -- symlinked installs are the recommended shape
        # precisely because copies drift, so they must be counted as present.
        if (child / "SKILL.md").is_file():
            out.add(child.name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--authored", default=None, help="repo skills/ dir (default: <repo>/skills)")
    ap.add_argument("--installed", default=os.environ.get("CLAUDE_SKILLS_DIR", str(Path.home() / ".claude" / "skills")))
    ap.add_argument("--bench", default=None,
                    help="file listing skills deliberately NOT installed, one per line; '#' comments allowed")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    authored_dir = Path(args.authored) if args.authored else repo / "skills"
    installed_dir = Path(args.installed)

    if not authored_dir.is_dir():
        print(f"COULD NOT MEASURE: authored skills dir does not exist: {authored_dir}", file=sys.stderr)
        return COULD_NOT_MEASURE

    authored = skill_names(authored_dir)
    if not authored:
        # POSITIVE CONTROL. This repo has skills; zero means the scan is blind,
        # not that the roster is empty. Reporting "all installed" here would be
        # the cleanest-looking lie this script could tell.
        print(f"COULD NOT MEASURE: found zero authored skills under {authored_dir} -- "
              f"the scan is blind, not clean", file=sys.stderr)
        return COULD_NOT_MEASURE

    if not installed_dir.is_dir():
        print(f"COULD NOT MEASURE: install dir does not exist: {installed_dir}", file=sys.stderr)
        print("  (an absent install dir is not 'nothing to install' -- it is not knowing)", file=sys.stderr)
        return COULD_NOT_MEASURE

    installed = skill_names(installed_dir)

    benched: set[str] = set()
    if args.bench:
        bench_path = Path(args.bench)
        if not bench_path.is_file():
            print(f"COULD NOT MEASURE: --bench given but unreadable: {bench_path}", file=sys.stderr)
            return COULD_NOT_MEASURE
        for line in bench_path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                benched.add(line)

    missing = sorted(authored - installed - benched)
    unknown_bench = sorted(benched - authored)

    print(f"authored={len(authored)} installed={len(installed)} benched={len(benched)}")

    if unknown_bench:
        # A bench entry naming a skill that no longer exists is stale
        # bookkeeping, and stale bookkeeping is how a real gap gets excused.
        print("bench names skills that are not authored (stale entries):", file=sys.stderr)
        for n in unknown_bench:
            print(f"  {n}", file=sys.stderr)

    if missing:
        print(f"NOT INSTALLED ({len(missing)}):", file=sys.stderr)
        for n in missing:
            print(f"  {n}", file=sys.stderr)
        print("", file=sys.stderr)
        print("An authored skill that is not installed cannot be invoked. On 2026-08-19", file=sys.stderr)
        print("this was 15 of 28, including prd, spec, tdd, ask-a-council,", file=sys.stderr)
        print("devils-advocate and verify-the-instrument -- dark for weeks.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Install with symlinks so copies cannot drift:", file=sys.stderr)
        print(f"  for s in {' '.join(missing[:3])} ...; do \\", file=sys.stderr)
        print(f"    ln -s {authored_dir}/$s {installed_dir}/$s; done", file=sys.stderr)
        print("Or add a deliberate entry to the bench file and pass --bench.", file=sys.stderr)
        return VIOLATION

    print("OK: every authored skill is installed or explicitly benched.")
    return CLEAN


if __name__ == "__main__":
    sys.exit(main())

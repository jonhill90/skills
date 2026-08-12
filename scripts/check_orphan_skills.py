#!/usr/bin/env python3
"""Advisory: report skills in this repo that no known roster accounts for.

jonhill90/skills#162. This repository can merge a skill, pass every CI job,
and have it install on no harness -- the roster that gates installation
lives in `agent-dotfiles` (`settings/default-skills.txt`), a different
repository. This script is this repository's own view into that question.

It is deliberately NOT authoritative and never fails the build: the roster
lives elsewhere, and this repository is not necessarily the only consumer.
See AGENTS.md's "What 'shipped' means" section.

The property that matters most: it degrades honestly. "The roster was not
reachable" and "checked, no orphans" are different exit codes and different
printed lines, on purpose. Reporting the former as the latter would be the
same blind spot agent-dotfiles#145 fixed for the skill description budget,
one layer over.

Exit codes (informational only -- see the `orphan-check` CI job, which runs
this with `continue-on-error: true` so none of these can fail a build):
  0  checked successfully, no orphans
  1  checked successfully, orphan(s) found
  2  could not check -- roster unreachable
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROSTER_URL = (
    "https://raw.githubusercontent.com/jonhill90/agent-dotfiles/main/"
    "settings/default-skills.txt"
)
BENCH_SECTION = "benched"


def parse_roster(text: str) -> tuple[set[str], set[str]]:
    """`default-skills.txt`'s format: flat skill names, optional
    `[section]` headers, and a special `[benched]` section whose lines are
    `name  # reason`. Mirrors agent-dotfiles' `scripts/sync.py`
    `_parse_skill_roster` closely enough to agree on membership; this
    script does not need modifiers or per-harness sections, only the union
    of every rostered name and every benched name.
    """
    rostered: set[str] = set()
    benched: set[str] = set()
    in_bench = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_bench = line[1:-1].strip().lower() == BENCH_SECTION
            continue
        name = line.split("#", 1)[0].strip()
        if not name:
            continue
        name = name.split()[0]  # drop a "+harness" modifier if present
        (benched if in_bench else rostered).add(name)
    return rostered, benched


def local_skill_names(skills_dir: Path) -> set[str]:
    if not skills_dir.is_dir():
        return set()
    return {
        p.name
        for p in skills_dir.iterdir()
        if p.is_dir() and (p / "SKILL.md").is_file()
    }


def find_orphans(names: set[str], rostered: set[str], benched: set[str]) -> list[str]:
    return sorted(names - rostered - benched)


def load_roster(
    roster_path: str | None,
    roster_url: str | None,
    opener=urllib.request.urlopen,
) -> tuple[str | None, str]:
    """Returns (text, source-description). text is None iff the roster
    could not be read -- the caller must treat that as "could not check",
    never as "no orphans"."""
    if roster_path:
        p = Path(roster_path)
        if not p.is_file():
            return None, f"local file not found: {p}"
        try:
            return p.read_text(encoding="utf-8"), f"local file {p}"
        except OSError as exc:
            return None, f"could not read local file {p}: {exc}"
    if not roster_url:
        return None, "no --roster-path given and network fetch disabled"
    try:
        with opener(roster_url, timeout=10) as response:
            return response.read().decode("utf-8"), roster_url
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return None, f"could not fetch {roster_url}: {exc}"


def run(
    skills_dir: Path,
    roster_path: str | None,
    roster_url: str | None,
    opener=urllib.request.urlopen,
    out=sys.stdout,
) -> int:
    names = local_skill_names(skills_dir)
    text, source = load_roster(roster_path, roster_url, opener=opener)

    if text is None:
        print(f"orphan-check: UNREACHABLE -- {source}", file=out)
        print(
            "orphan-check: this is NOT the same as a clean result -- the "
            "roster was not visible from here, so nothing was checked",
            file=out,
        )
        return 2

    rostered, benched = parse_roster(text)
    orphans = find_orphans(names, rostered, benched)

    print(f"orphan-check: roster read from {source}", file=out)
    if orphans:
        print(
            f"orphan-check: {len(orphans)} skill(s) neither rostered nor "
            "benched:",
            file=out,
        )
        for name in orphans:
            print(f"  {name}", file=out)
        return 1

    print(f"orphan-check: CLEAN -- all {len(names)} skill(s) accounted for", file=out)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--roster-path",
        default=None,
        help="local path to a default-skills.txt (e.g. from an "
        "agent-dotfiles checkout); skips the network fetch",
    )
    parser.add_argument(
        "--roster-url",
        default=ROSTER_URL,
        help="fetched only when --roster-path is not given",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="never fetch --roster-url; used when only --roster-path "
        "should be trusted",
    )
    parser.add_argument(
        "--skills-dir",
        default=None,
        help="defaults to <repo-root>/skills",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    skills_dir = Path(args.skills_dir) if args.skills_dir else repo_root / "skills"
    roster_url = None if args.no_network else args.roster_url

    return run(skills_dir, args.roster_path, roster_url)


if __name__ == "__main__":
    sys.exit(main())

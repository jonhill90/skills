#!/usr/bin/env python3
"""Confirm a skill is actually installed on this machine's shared skills
path AND matches this repository's own current copy of it -- a local
filesystem comparison, no network, no private-harness access.

Why this exists (jonhill90/skills#230's evaluation loop, #244's own
full-population diagnosis): four independent evaluation passes each
rediscovered the SAME failure mode by hand, one at a time --
`durable-fact-before-label`, `spec-driven-development`,
`test-in-the-consumer-context`, and `wire-it-when-you-write-it` were each
evaluated once against a machine where the skill under test was not
actually on `~/.claude/skills/` at all. Every case silently made the
"with the skill" arm ALSO a without-the-skill run -- caught only because
a human noticed a suspiciously short, cheap run and investigated by hand.
A written checklist item in `docs/evals.md` gets skipped exactly as
reliably as the four passes skipped noticing this; this script is the
mechanical version, wired into `eval_status.py --record` (see that
script's own doc comment) so recording a verdict cannot proceed on an
unchecked or broken install without an explicit, loud, named override.

MISSING and DIVERGENT are reported as distinct failures on purpose --
"the skill was never symlinked in at all" and "the skill IS present but
its content has drifted from what this repo currently ships" are
different problems with different fixes (symlink it in, versus figure
out why a real copy exists and disagrees). Collapsing them into one
"bad install" message would throw away exactly the distinction a human
fixing this needs first.

A symlinked skill (this repo's own normal installation shape --
`~/.claude/skills/<name>` -> a checkout of this repo's own `skills/<name>`)
is resolved through the symlink and compared by content like any other
directory, not trusted merely for being a symlink: a symlink into a stale
checkout, or one pointed at the wrong branch, is exactly as divergent as
a plain copied directory would be, and must be reported as such.

Python 3 stdlib only (matches this repository's other scripts/*.py).
"""

from __future__ import annotations

import argparse
import filecmp
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO / "skills"

MISSING = "missing"
DIVERGENT = "divergent"
OK = "ok"

EXIT_OK = 0
EXIT_MISSING = 2
EXIT_DIVERGENT = 3
EXIT_COULD_NOT_CHECK = 4

_EXIT_FOR_STATUS = {OK: EXIT_OK, MISSING: EXIT_MISSING, DIVERGENT: EXIT_DIVERGENT}


@dataclass
class InstallCheck:
    skill: str
    status: str  # OK | MISSING | DIVERGENT
    message: str
    # Populated only for DIVERGENT: relative paths present in one tree and
    # not the other, or present in both with different content -- the
    # detail a human needs to tell "never installed the update" apart
    # from "someone hand-edited the installed copy."
    only_in_installed: list[str] = field(default_factory=list)
    only_in_repo: list[str] = field(default_factory=list)
    differing: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        return _EXIT_FOR_STATUS[self.status]


def _relative_file_set(root: Path) -> set[str]:
    return {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file()
    }


def check_installed(skill: str, claude_skills_dir: Path, repo_root: Path = REPO) -> InstallCheck:
    """The one comparison this module owns: does `claude_skills_dir/skill`
    exist (following a symlink if it is one) and match
    `repo_root/skills/skill` byte-for-byte, file-for-file?

    Raises ValueError (never returns a check for it) if `skill` has no
    directory under `repo_root/skills/` at all -- that is a caller error
    (checking a name that isn't a skill), not an install-state finding,
    the same "refuse rather than guess" rule `eval_status.py`'s own
    `do_record` already applies to an unknown skill name.
    """
    repo_copy = repo_root / "skills" / skill
    if not repo_copy.is_dir():
        raise ValueError(f"{skill!r} has no skills/{skill}/ directory in {repo_root} -- not a real skill")

    installed = claude_skills_dir / skill
    # exists() follows symlinks and returns False for a dangling one --
    # exactly "missing" from this check's own point of view; a symlink
    # pointing at nothing is not installed in any sense that matters here.
    if not installed.exists():
        return InstallCheck(
            skill=skill,
            status=MISSING,
            message=(
                f"{skill}: MISSING -- {installed} does not exist "
                f"(not on the shared skills path at all)"
            ),
        )

    installed_files = _relative_file_set(installed)
    repo_files = _relative_file_set(repo_copy)

    only_in_installed = sorted(installed_files - repo_files)
    only_in_repo = sorted(repo_files - installed_files)

    differing = []
    for rel in sorted(installed_files & repo_files):
        if not filecmp.cmp(installed / rel, repo_copy / rel, shallow=False):
            differing.append(rel)

    if only_in_installed or only_in_repo or differing:
        parts = []
        if only_in_repo:
            parts.append(f"{len(only_in_repo)} file(s) missing from the installed copy")
        if only_in_installed:
            parts.append(f"{len(only_in_installed)} file(s) present only in the installed copy")
        if differing:
            parts.append(f"{len(differing)} file(s) with different content")
        return InstallCheck(
            skill=skill,
            status=DIVERGENT,
            message=f"{skill}: DIVERGENT -- {'; '.join(parts)} (installed={installed}, repo={repo_copy})",
            only_in_installed=only_in_installed,
            only_in_repo=only_in_repo,
            differing=differing,
        )

    return InstallCheck(
        skill=skill,
        status=OK,
        message=f"{skill}: OK -- installed copy at {installed} matches {repo_copy}",
    )


def default_claude_skills_dir() -> Path:
    home = Path.home()
    return home / ".claude" / "skills"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("skill", help="skill name, matches a skills/<name>/ directory in this repo")
    ap.add_argument("--claude-skills-dir", default=None,
                     help="path to the shared skills directory to check "
                          "(default: ~/.claude/skills)")
    ap.add_argument("--repo-root", default=str(REPO),
                     help="path to the skills-repo checkout to compare against "
                          "(default: this script's own repo)")
    args = ap.parse_args(argv)

    claude_skills_dir = Path(args.claude_skills_dir) if args.claude_skills_dir else default_claude_skills_dir()
    repo_root = Path(args.repo_root)

    try:
        result = check_installed(args.skill, claude_skills_dir, repo_root)
    except ValueError as exc:
        print(f"COULD-NOT-CHECK: {exc}", file=sys.stderr)
        return EXIT_COULD_NOT_CHECK

    stream = sys.stdout if result.status == OK else sys.stderr
    print(result.message, file=stream)
    for rel in result.only_in_repo:
        print(f"  missing:   {rel}", file=stream)
    for rel in result.only_in_installed:
        print(f"  extra:     {rel}", file=stream)
    for rel in result.differing:
        print(f"  differs:   {rel}", file=stream)
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

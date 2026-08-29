#!/usr/bin/env python3
"""The one canonical tally of skills/*/references/eval-result.md verdicts
(jonhill90/skills#294, vocabulary split by #296).

Why this exists: the obvious command --

    grep -rhE '^\\**[Vv]erdict\\**:' skills/*/references/eval-result.md | wc -l

-- counts every line that LOOKS like a verdict, including verdicts from a
SUPERSEDED earlier pass that a file deliberately keeps for the human record
(this repository's whole point is not destroying evaluation evidence to make
a count come out clean -- see skills/mine-transcripts and skills/tmux, both
re-run more than once). That grep returns 43 across 41 files -- inflating
`could_not_measure` by exactly the two superseded lines, in the same
direction as the miscount jonhill90/skills#289 and #290 were about. The real,
current-verdict-only tally on this tree is:

     3 could_not_measure
    20 no_effect_observed
     3 scenario_inadequate
    11 improve
     3 keep
     1 drop           (= 41)

A superseded verdict is marked "Previous verdict:" (capital P, not
"Verdict:") specifically so it keeps reading as prose to a human -- nothing
about the historical record changes -- while no longer matching the pattern
below. That is the whole fix: one line's label, not a second file to keep in
sync, not a parser that has to guess which line is "the real one" by
position. `find_verdict_problems` below still checks the position invariant
(exactly one canonical line, and it must be the file's first non-blank,
non-heading line) so a future edit that reintroduces a second "Verdict:"
line -- rather than remembering to write "Previous verdict:" -- is caught
here rather than silently re-inflating the count the way the naive grep did.

`could_not_measure` used to be 26 of 41 -- one number standing in for three
different situations (jonhill90/skills#296). Reading each of those 26
bodies rather than pattern-matching the verdict line split it three ways:

  - `could_not_measure` (3 left) -- genuinely blind: the harness could not
    confirm the skill was ever exercised (an install-path gap, or -- for
    `github-cli`/`linear`/`obsidian` -- a "with" arm delivered the skill by
    prompt instruction with no independent confirmation it was read). A
    re-run with that confirmation fixed can still produce a real verdict.
  - `no_effect_observed` (20) -- measured cleanly, both arms behaved the
    same. This is a finding, not an absence: it says the base model already
    does the thing this skill asks for, on the scenario tested. It is NOT
    grounds to drop the skill -- a null result on one scenario is evidence
    about that scenario, not about the skill's value on a harder one.
  - `scenario_inadequate` (3) -- the scenario itself never discriminated
    and re-running it will not fix that; it needs a different scenario (or
    an honest statement that this skill's effect is not A/B-measurable on
    a single task). Distinct from a blind case: nothing stopped the harness
    from exercising the skill here, the exercise just didn't engage the
    thing being tested.

No skill's keep/improve/drop judgement changed here -- this relabels *why*
a `could_not_measure` was could_not_measure, never converts one verdict
family into another. See jonhill90/skills#296's closing PR for the
per-skill classification table and reasoning.

scripts/validate_repository.py imports `find_verdict_problems` from this
module and fails the build on any problem it returns
(jonhill90/skills#294's own acceptance test: add a second `Verdict:` line to
any eval-result.md and the validator must go red; remove it and it must go
green). This module owns the parsing; validate_repository.py owns turning a
problem into a build failure -- same split as check_orphan_skills.py /
check_skill_install.py in this same directory.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO / "skills"

# Matches ONLY an authoritative verdict line -- "**Verdict: <token>...**" --
# never "**Previous verdict: ...**" (starts with "Previous", not "Verdict")
# and never a line that merely mentions the word in prose (must be the first
# thing on the line, modulo leading "**"). Case-sensitive on purpose: every
# verdict line in this collection capitalizes "Verdict"; a stray lowercase
# "verdict:" opener is exactly the kind of drift this ought to flag by
# failing to match, not by silently accepting a second shape.
VERDICT_LINE_RE = re.compile(r"^\**Verdict\**:\s*([a-z_]+)")


def eval_result_files(skills_root: Path = SKILLS_ROOT) -> list[Path]:
    return sorted(skills_root.glob("*/references/eval-result.md"))


def canonical_verdict_lines(text: str) -> list[str]:
    """Every line in `text` that reads as an authoritative verdict. A
    well-formed eval-result.md has exactly one."""
    return [
        line.strip()
        for line in text.splitlines()
        if VERDICT_LINE_RE.match(line.strip())
    ]


def verdict_token(line: str) -> str | None:
    match = VERDICT_LINE_RE.match(line.strip())
    return match.group(1) if match else None


def find_verdict_problems(skills_root: Path = SKILLS_ROOT) -> list[str]:
    """Returns one problem string per eval-result.md that does not carry
    exactly one authoritative verdict line. Empty means every file is
    countable unambiguously -- the precondition tally() relies on."""
    problems = []
    for path in eval_result_files(skills_root):
        lines = canonical_verdict_lines(path.read_text(encoding="utf-8"))
        rel = path.relative_to(skills_root.parent) if skills_root.is_absolute() else path
        if len(lines) == 0:
            problems.append(f"{rel}: no authoritative \"Verdict:\" line found")
        elif len(lines) > 1:
            problems.append(
                f"{rel}: {len(lines)} \"Verdict:\" lines found (expected 1) -- "
                "mark any superseded pass as \"Previous verdict:\" instead"
            )
    return problems


def tally(skills_root: Path = SKILLS_ROOT) -> Counter:
    """Counts exactly one verdict per file -- its first (and, once
    find_verdict_problems reports clean, only) authoritative line."""
    counts: Counter = Counter()
    for path in eval_result_files(skills_root):
        lines = canonical_verdict_lines(path.read_text(encoding="utf-8"))
        if not lines:
            continue
        token = verdict_token(lines[0])
        if token:
            counts[token] += 1
    return counts


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    ap.parse_args(argv)

    problems = find_verdict_problems(SKILLS_ROOT)
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)

    counts = tally(SKILLS_ROOT)
    total = sum(counts.values())
    for verdict in sorted(counts):
        print(f"{verdict}: {counts[verdict]}")
    print(f"total: {total}")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

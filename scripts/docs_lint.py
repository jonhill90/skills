#!/usr/bin/env python3
"""Enforce the docs layout (docs/decisions/0001-documentation-layout.md):
three rules, all hard failures, none advisory. Which subject directory a
document belongs in is a human judgment call; this script never re-decides
it. It only enforces the structural invariants that call depends on:

  1. No unfiled root file directly under docs/ -- every document lives in
     one of SUBJECT_DIRS, or is named on the ROOT_ALLOWLIST below with a
     stated reason. An allowlist entry is a genuine entry point, never a
     place to dump a new file to dodge filing. A SYMLINK at the root is
     also recognized: a compat pointer for an external consumer that
     hardcodes the old path. Rule 2 independently verifies it points
     outside docs/, so rule 1 does not re-litigate that. Prose pointer
     stubs are not recognized: git history is the archive.
  2. No state file (.json/.jsonl) anywhere under docs/, recursively --
     generated/derived state does not belong in a documentation tree.
     The one exception is a SYMLINK whose target resolves OUTSIDE docs/
     entirely: that is a compatibility pointer for an external consumer
     that hardcodes the old path (e.g. a sibling repo's own constant),
     not state living in docs/ a second time. A symlink whose target
     still resolves inside docs/, or a broken symlink, is not exempt --
     both would be exactly the "state file in docs/" shape in disguise.
  3. Zero full-text duplicates by checksum, across every tracked .md and
     .py file in the repo (not scoped to docs/ alone -- a duplicate is a
     duplicate wherever it sits, and P11's own refutation of the prior
     "duplicates" claim already used this same scope). Scoped to files
     `git ls-files` reports (the committed/staged tree), same as CI sees
     it -- an untracked scratch file is not yet part of the repo this
     rule protects.

Every check function below takes `repo` (the root to check) as its own
parameter, never reads a module-level default internally -- the same
shape `scripts/skills_table.py`'s own functions use, and for the same
reason: `tests/test_docs_lint.py` points these at a throwaway fixture
directory, never this repository's own tree, so a broken rule can be
proven broken without ever touching real content.

Exit 0 = all three rules hold. Exit 1 = at least one violation, printed
with the specific path so a fix is mechanical, not a re-investigation.
This script does not repair anything.

Run: python3 scripts/docs_lint.py
"""
from __future__ import annotations
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Genuine entry points a reader expects directly under docs/, never a
# classification dodge. Each entry needs a reason here before it's added.
ROOT_ALLOWLIST = {
    "README.md": "the docs/ index itself -- the one signpost that links "
                  "every reference page and decision record.",
}

SUBJECT_DIRS = {"reference", "decisions"}


def check_unclassified_root_files(repo: Path) -> list[str]:
    """Rule 1: every direct child of docs/ is a subject directory, a file
    named on ROOT_ALLOWLIST, or a compat symlink. Nothing else."""
    docs = repo / "docs"
    violations = []
    if not docs.is_dir():
        return violations
    for entry in sorted(docs.iterdir()):
        if entry.is_dir():
            if entry.name not in SUBJECT_DIRS:
                violations.append(
                    f"docs/{entry.name}/: unrecognized top-level directory "
                    f"(expected one of {sorted(SUBJECT_DIRS)})")
            continue
        if entry.name in ROOT_ALLOWLIST:
            continue
        if entry.is_symlink():
            continue  # rule 2 verifies the target is a real compat pointer
        violations.append(
            f"docs/{entry.name}: unfiled root file -- move it into "
            f"docs/reference/ or docs/decisions/, or add it to "
            f"ROOT_ALLOWLIST in this script with a reason")
    return violations


def check_no_state_files_in_docs(repo: Path) -> list[str]:
    """Rule 2: no .json/.jsonl anywhere under docs/, recursively, unless
    it is a symlink whose target resolves outside docs/ entirely."""
    docs = repo / "docs"
    violations = []
    if not docs.is_dir():
        return violations
    docs_resolved = docs.resolve()
    for p in sorted(docs.rglob("*")):
        if p.suffix not in (".json", ".jsonl"):
            continue
        rel = p.relative_to(repo)
        if p.is_symlink():
            try:
                target = p.resolve(strict=True)
            except OSError:
                violations.append(
                    f"{rel}: broken symlink -- a dangling "
                    f"compat pointer is not a valid exception")
                continue
            try:
                target.relative_to(docs_resolved)
                still_in_docs = True
            except ValueError:
                still_in_docs = False
            if still_in_docs:
                violations.append(
                    f"{rel}: symlink target still resolves "
                    f"inside docs/ -- not a real compat pointer, this is a "
                    f"state file in docs/ wearing a symlink")
            continue
        violations.append(
            f"{rel}: state file under docs/ -- relocate it "
            f"outside docs/; generated data does not belong in a "
            f"documentation tree")
    return violations


def check_zero_duplicate_checksums(repo: Path) -> list[str]:
    """Rule 3: no two tracked .md/.py files share a sha256 of their full
    byte content. Scope is the whole repo, not just docs/ -- matches the
    scope P11's own duplicate-refutation used."""
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "*.md", "*.py"],
        capture_output=True, text=True, check=True,
    ).stdout
    by_hash: dict[str, list[str]] = {}
    for rel in out.splitlines():
        if not rel.strip():
            continue
        path = repo / rel
        if path.is_symlink() or not path.is_file():
            # A symlink (e.g. CLAUDE.md -> AGENTS.md, the multi-harness
            # entry-point convention) is an ALIAS to one real file, not an
            # independent copy that can drift -- comparing its resolved
            # bytes against its own target would always "find" a
            # duplicate that isn't one. Only real, independent files can
            # be a genuine full-text duplicate.
            continue
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        by_hash.setdefault(h, []).append(rel)
    violations = []
    for h, paths in sorted(by_hash.items()):
        if len(paths) > 1:
            violations.append(
                f"full-text duplicate (sha256 {h[:12]}): {', '.join(sorted(paths))}")
    return violations


def run(repo: Path) -> tuple[int, list[str]]:
    """Runs all three checks against repo, returns (exit_code, printed
    lines) -- factored out of main() so tests exercise the same code path
    the CLI does, not a re-implementation of it."""
    checks = [
        ("no unfiled root files under docs/", check_unclassified_root_files),
        ("no state files under docs/", check_no_state_files_in_docs),
        ("zero full-text duplicates by checksum", check_zero_duplicate_checksums),
    ]
    lines = []
    total = 0
    for label, fn in checks:
        violations = fn(repo)
        if violations:
            lines.append(f"FAIL -- {label} ({len(violations)}):")
            for v in violations:
                lines.append(f"  - {v}")
        else:
            lines.append(f"ok   -- {label}")
        total += len(violations)
    lines.append("")
    if total:
        lines.append(f"docs-lint: {total} violation(s). Fix them; this script does not repair anything.")
        return 1, lines
    lines.append("docs-lint: all three rules hold.")
    return 0, lines


def main() -> int:
    code, lines = run(REPO)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())

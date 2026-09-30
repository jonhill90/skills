#!/usr/bin/env python3
"""Check the mechanical parts of a repository's layout.

Reports only rules a script can decide without judgment:

  entry-point       README.md at the root (error); AGENTS.md at the root (warning)
  instruction-file  AGENTS.md is canonical; CLAUDE.md is a symlink to it or imports it
  placeholder-dir   a directory kept alive only by .gitkeep/.keep
  pytest-basename   duplicate test file names that pytest's default import mode rejects
  mintlify-exposed  a page under a Mintlify root that is neither in navigation nor ignored

Placement decisions (is this the right home for that feature?) need judgment and
are out of scope. Standard library only.

Exit codes: 0 no errors (warnings allowed), 1 errors found, 2 could not check.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", ".tox", ".nox",
    "dist", "build", "site-packages", ".mypy_cache", ".pytest_cache", ".ruff_cache",
}
PLACEHOLDER_FILES = {".gitkeep", ".keep"}
PYTEST_CONFIG_FILES = ("pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini")
IMPORTLIB_MODE_RE = re.compile(r"import-mode[\s=]+importlib")
# Files Mintlify never publishes (https://www.mintlify.com/docs/organize/mintignore).
MINTLIFY_DEFAULT_IGNORED = {"README.md", "LICENSE.md", "CHANGELOG.md", "CONTRIBUTING.md"}


@dataclass(frozen=True)
class Finding:
    severity: str  # "error" or "warning"
    rule: str
    path: Path
    message: str


def walk(root: Path):
    """Yield (directory, subdirectory names, file names), skipping tool output."""
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        yield Path(current), dirs, sorted(files)


# --- entry points and instruction files -------------------------------------

def check_entry_points(root: Path) -> list[Finding]:
    findings = []
    if not (root / "README.md").exists():
        findings.append(Finding("error", "entry-point", root, "no README.md at the repository root"))
    if not (root / "AGENTS.md").exists():
        findings.append(Finding("warning", "entry-point", root, "no AGENTS.md at the repository root"))
    return findings


def check_instruction_files(root: Path) -> list[Finding]:
    agents, claude = root / "AGENTS.md", root / "CLAUDE.md"
    if not (agents.exists() and claude.exists()):
        return []
    if agents.is_symlink() and not claude.is_symlink():
        return [Finding(
            "warning", "instruction-file", agents,
            "AGENTS.md is a symlink to CLAUDE.md; make AGENTS.md the real file and "
            "CLAUDE.md the symlink or an @AGENTS.md import",
        )]
    if claude.is_symlink():
        return []
    if "@AGENTS.md" in claude.read_text(errors="ignore"):
        return []
    return [Finding(
        "warning", "instruction-file", claude,
        "CLAUDE.md and AGENTS.md are independent files that can drift; "
        "start CLAUDE.md with @AGENTS.md or symlink it",
    )]


# --- placeholders -----------------------------------------------------------

def check_placeholders(root: Path) -> list[Finding]:
    findings = []
    for current, dirs, files in walk(root):
        if current != root and not dirs and files and set(files) <= PLACEHOLDER_FILES:
            findings.append(Finding(
                "warning", "placeholder-dir", current,
                "directory exists only to hold a placeholder; create it when it has content",
            ))
    return findings


# --- pytest -----------------------------------------------------------------

def importlib_mode_configured(root: Path) -> bool:
    return any(
        IMPORTLIB_MODE_RE.search((root / name).read_text(errors="ignore"))
        for name in PYTEST_CONFIG_FILES
        if (root / name).is_file()
    )


def is_test_file(name: str) -> bool:
    return name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py"))


def check_pytest_basenames(root: Path) -> list[Finding]:
    # Not gated on detecting pytest: it is often installed without being named
    # in any config file. Under its default "prepend" mode a test file outside
    # a package is imported by its bare basename, so two such files collide.
    if importlib_mode_configured(root):
        return []
    by_name: dict[str, list[Path]] = {}
    for current, _, files in walk(root):
        if "__init__.py" in files:
            continue
        for name in files:
            if is_test_file(name):
                by_name.setdefault(name, []).append(current / name)
    findings = []
    for name, paths in sorted(by_name.items()):
        if len(paths) > 1:
            others = ", ".join(str(p.relative_to(root)) for p in paths[1:])
            findings.append(Finding(
                "error", "pytest-basename", paths[0],
                f"{name} also exists at {others}; pytest's default import mode fails "
                "to collect both. Set --import-mode=importlib or add __init__.py files",
            ))
    return findings


# --- Mintlify ---------------------------------------------------------------

def mintlify_roots(root: Path) -> list[Path]:
    roots = []
    for current, _, files in walk(root):
        for name in ("docs.json", "mint.json"):
            if name not in files:
                continue
            try:
                config = json.loads((current / name).read_text())
            except (OSError, ValueError):
                continue
            if isinstance(config, dict) and "navigation" in config:
                roots.append(current)
                break
    return roots


def navigation_pages(node) -> set[str]:
    pages: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "pages" and isinstance(value, list):
                pages.update(v.strip("/") for v in value if isinstance(v, str))
            pages |= navigation_pages(value)
    elif isinstance(node, list):
        for value in node:
            pages |= navigation_pages(value)
    return pages


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def parse_ignore(text: str) -> list[tuple[bool, bool, bool, re.Pattern[str]]]:
    """Parse the .gitignore subset .mintignore uses: (negated, anchored, dir_only, regex)."""
    rules = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        negated = line.startswith("!")
        line = line[1:] if negated else line
        dir_only = line.endswith("/")
        line = line.rstrip("/")
        anchored = "/" in line
        rules.append((negated, anchored, dir_only, glob_to_regex(line.lstrip("/"))))
    return rules


def ignored(rules, rel: str, is_dir: bool) -> bool:
    result = False
    for negated, anchored, dir_only, regex in rules:
        if dir_only and not is_dir:
            continue
        subject = rel if anchored else rel.rsplit("/", 1)[-1]
        if regex.match(subject):
            result = not negated
    return result


def excluded(rules, rel: str) -> bool:
    # As in git, a file cannot be re-included once a parent directory is excluded.
    parts = rel.split("/")
    for depth in range(1, len(parts)):
        if ignored(rules, "/".join(parts[:depth]), is_dir=True):
            return True
    return ignored(rules, rel, is_dir=False)


def check_mintlify(root: Path) -> list[Finding]:
    findings = []
    for site in mintlify_roots(root):
        config_name = "docs.json" if (site / "docs.json").exists() else "mint.json"
        pages = navigation_pages(json.loads((site / config_name).read_text()).get("navigation"))
        ignore_file = site / ".mintignore"
        rules = parse_ignore(ignore_file.read_text()) if ignore_file.is_file() else []
        for current, dirs, files in walk(site):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for name in files:
                if not name.endswith((".md", ".mdx")) or name in MINTLIFY_DEFAULT_IGNORED:
                    continue
                rel = (current / name).relative_to(site).as_posix()
                if rel.rsplit(".", 1)[0] in pages or excluded(rules, rel):
                    continue
                findings.append(Finding(
                    "warning", "mintlify-exposed", current / name,
                    f"not in {config_name} navigation but still published by URL; "
                    "add it to navigation or exclude it in .mintignore",
                ))
    return findings


# --- entry ------------------------------------------------------------------

CHECKS = (
    check_entry_points,
    check_instruction_files,
    check_placeholders,
    check_pytest_basenames,
    check_mintlify,
)


def check(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for run in CHECKS:
        findings.extend(run(root))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", nargs="?", default=".", help="repository root (default: .)")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"cannot check: {root} is not a directory")
        return 2

    findings = check(root)
    if args.json:
        print(json.dumps(
            [
                {"severity": f.severity, "rule": f.rule,
                 "path": f.path.relative_to(root).as_posix() or ".", "message": f.message}
                for f in findings
            ],
            indent=2,
        ))
    else:
        for f in findings:
            print(f"{f.severity}: {f.rule}: {f.path.relative_to(root).as_posix() or '.'}: {f.message}")
        errors = sum(f.severity == "error" for f in findings)
        print(f"Checked {root}: {errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())

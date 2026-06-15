#!/usr/bin/env python3
"""Validate portable skills and repository compatibility projections."""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import yaml


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
PORTABLE_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
EXECUTABLE_SUFFIXES = {".py", ".sh", ".bash"}
EXPECTED_PROJECTIONS = {
    ".agents/skills": "../skills",
    ".claude/skills": "../skills",
    ".codex/skills": "../skills",
    ".claude/agents": "../agents",
    ".codex/agents": "../agents",
    ".github/agents": "../agents",
}


@dataclass(frozen=True)
class Finding:
    level: str
    path: Path
    message: str


def parse_skill(skill_file: Path) -> tuple[dict[str, object], str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with ---")

    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("SKILL.md has unclosed YAML frontmatter") from exc

    frontmatter = yaml.safe_load("\n".join(lines[1:closing]))
    if not isinstance(frontmatter, dict):
        raise ValueError("frontmatter must be a YAML mapping")

    return frontmatter, "\n".join(lines[closing + 1 :]).strip()


def local_link_target(skill_file: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None

    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target:
        return None
    return skill_file.parent / target


def validate_skill(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.is_file():
        return [Finding("error", skill_dir, "missing SKILL.md")]

    try:
        frontmatter, body = parse_skill(skill_file)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        return [Finding("error", skill_file, str(exc))]

    unknown_fields = sorted(set(frontmatter) - PORTABLE_FIELDS)
    if unknown_fields:
        findings.append(
            Finding(
                "error",
                skill_file,
                f"non-portable frontmatter fields: {', '.join(unknown_fields)}",
            )
        )

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name:
        findings.append(Finding("error", skill_file, "name must be a non-empty string"))
    else:
        if len(name) > 64:
            findings.append(Finding("error", skill_file, "name exceeds 64 characters"))
        if not NAME_RE.fullmatch(name):
            findings.append(
                Finding("error", skill_file, "name must use lowercase kebab-case")
            )
        if name != skill_dir.name:
            findings.append(
                Finding(
                    "error",
                    skill_file,
                    f"name {name!r} does not match directory {skill_dir.name!r}",
                )
            )

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        findings.append(
            Finding("error", skill_file, "description must be a non-empty string")
        )
    elif len(description) > 1024:
        findings.append(
            Finding("error", skill_file, "description exceeds 1024 characters")
        )

    if not body:
        findings.append(Finding("error", skill_file, "skill body is empty"))

    line_count = len(skill_file.read_text(encoding="utf-8").splitlines())
    if line_count > 500:
        findings.append(
            Finding(
                "warning",
                skill_file,
                f"SKILL.md has {line_count} lines; prefer fewer than 500",
            )
        )

    if (skill_dir / "README.md").exists():
        findings.append(
            Finding("error", skill_dir / "README.md", "skill directories cannot contain README.md")
        )

    for raw_target in LINK_RE.findall(body):
        target = local_link_target(skill_file, raw_target)
        if target is not None and not target.exists():
            findings.append(
                Finding(
                    "error",
                    skill_file,
                    f"relative link does not resolve: {raw_target}",
                )
            )

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(path for path in scripts_dir.rglob("*") if path.is_file()):
            if script.suffix in EXECUTABLE_SUFFIXES and not os.access(script, os.X_OK):
                findings.append(
                    Finding("error", script, "script must have an executable mode")
                )

    return findings


def discover_skill_dirs(root: Path, target: Path | None) -> list[Path]:
    if target is None:
        skills_root = root / "skills"
        return sorted(path for path in skills_root.iterdir() if path.is_dir())

    target = target.resolve()
    if target.name == "SKILL.md":
        target = target.parent
    if (target / "SKILL.md").is_file():
        return [target]
    if target.name == "skills" and target.is_dir():
        return sorted(path for path in target.iterdir() if path.is_dir())
    raise ValueError(f"target is not a skill directory or skills root: {target}")


def validate_projections(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for relative_path, expected_target in EXPECTED_PROJECTIONS.items():
        projection = root / relative_path
        if not projection.is_symlink():
            findings.append(
                Finding("error", projection, "expected compatibility symlink")
            )
            continue
        actual_target = os.readlink(projection)
        if actual_target != expected_target:
            findings.append(
                Finding(
                    "error",
                    projection,
                    f"expected -> {expected_target}, found -> {actual_target}",
                )
            )
        elif not projection.exists():
            findings.append(Finding("error", projection, "symlink target is broken"))
    return findings


def validate_skill_collection(skill_dirs: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    names: dict[str, Path] = {}

    for skill_dir in skill_dirs:
        findings.extend(validate_skill(skill_dir))
        try:
            frontmatter, _ = parse_skill(skill_dir / "SKILL.md")
        except (OSError, UnicodeError, yaml.YAMLError, ValueError):
            continue
        name = frontmatter.get("name")
        if isinstance(name, str):
            previous = names.get(name)
            if previous is not None:
                findings.append(
                    Finding(
                        "error",
                        skill_dir / "SKILL.md",
                        f"duplicate skill name {name!r}; first declared in {previous}",
                    )
                )
            else:
                names[name] = skill_dir / "SKILL.md"

    return findings


def validate(root: Path, target: Path | None = None) -> list[Finding]:
    skill_dirs = discover_skill_dirs(root, target)
    findings = validate_skill_collection(skill_dirs)

    if target is None:
        findings.extend(validate_projections(root))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        nargs="?",
        type=Path,
        help="optional skill directory, SKILL.md, or skills root",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    target = args.target
    if target is not None and not target.is_absolute():
        target = root / target

    try:
        findings = validate(root, target)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    for finding in findings:
        try:
            display_path = finding.path.relative_to(root)
        except ValueError:
            display_path = finding.path
        print(f"{finding.level.upper()}: {display_path}: {finding.message}")

    error_count = sum(finding.level == "error" for finding in findings)
    warning_count = sum(finding.level == "warning" for finding in findings)
    skill_count = len(discover_skill_dirs(root, target))
    print(
        f"Validated {skill_count} skill(s): "
        f"{error_count} error(s), {warning_count} warning(s)"
    )
    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())

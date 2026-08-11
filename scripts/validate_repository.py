#!/usr/bin/env python3
"""Validate the portable Agent Skills in this repository."""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:  # fresh machines lack PyYAML; use the fallback parser
    yaml = None

YAML_ERRORS = (yaml.YAMLError,) if yaml is not None else ()
PARSE_ERRORS = (OSError, UnicodeError, ValueError) + YAML_ERRORS


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

# AGENTS.md caps SKILL.md at 500 lines. Enforced since 2026-07-27: it was a
# convention before, and skills/tmux reached 493 lines with nobody notified.
# The warning band exists because "seven lines from breaking" and "fine"
# look identical in a diff.
SKILL_LINE_CAP = 500
SKILL_LINE_WARN = 450


@dataclass(frozen=True)
class Finding:
    level: str
    path: Path
    message: str


def mini_yaml(text: str) -> dict[str, object]:
    """Minimal fallback for flat `key: value` frontmatter when PyYAML is
    unavailable (fresh machines). Handles quoted values and comments;
    values keep embedded colons verbatim."""
    parsed: dict[str, object] = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        parsed[key.strip()] = value
    return parsed


def _quote_colon_value(line: str) -> str:
    """Quote a flat 'key: value' line's value when it contains an embedded
    colon. SKILL.md frontmatter is always flat key/value pairs — never
    nested mappings or flow collections — so a bare colon in a value (e.g.
    "runs long: repetition, not duration") is content, not a second mapping
    separator. Plain YAML disagrees: unquoted ': ' inside a scalar is a
    parse error, and PyYAML's message ("mapping values are not allowed
    here") does not name the colon as the cause (jonhill90/skills#142).
    Quoting the value here — before either parser sees it — makes a colon
    in a description "just work" without the author having to know to
    quote it, and keeps the PyYAML and mini_yaml backends in agreement."""
    if not line or line[0].isspace() or line.lstrip().startswith("#"):
        return line
    key, sep, value = line.partition(":")
    if not sep:
        return line
    stripped = value.strip()
    if not stripped or ":" not in stripped:
        return line
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in "'\"":
        return line  # already quoted
    if stripped[0] in "[{":
        return line  # flow collection — leave to the real parser
    escaped = stripped.replace("\\", "\\\\").replace('"', '\\"')
    return f'{key}: "{escaped}"'


def normalize_frontmatter(raw: str) -> str:
    return "\n".join(_quote_colon_value(line) for line in raw.splitlines())


def parse_skill(skill_file: Path) -> tuple[dict[str, object], str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with ---")

    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("SKILL.md has unclosed YAML frontmatter") from exc

    raw = normalize_frontmatter("\n".join(lines[1:closing]))
    frontmatter = yaml.safe_load(raw) if yaml else mini_yaml(raw)
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
    except PARSE_ERRORS as exc:
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


def validate_skill_length(skill_dir: Path) -> list[Finding]:
    """Keep SKILL.md within the cap, and say so before it is breached."""
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return []
    lines = len(path.read_text(encoding="utf-8").splitlines())
    if lines > SKILL_LINE_CAP:
        return [Finding(
            "error", path,
            f"{lines} lines exceeds the {SKILL_LINE_CAP}-line cap — move "
            "detail into references/ (progressive disclosure)",
        )]
    if lines > SKILL_LINE_WARN:
        return [Finding(
            "warning", path,
            f"{lines} lines, approaching the {SKILL_LINE_CAP}-line cap — "
            "move detail into references/ before it breaks",
        )]
    return []


def validate_privacy(root: Path) -> list[Finding]:
    """Flag tracked markdown containing terms from the untracked
    .privacy-denylist (one term per line; the terms never enter git)."""
    denylist_file = root / ".privacy-denylist"
    if not denylist_file.is_file():
        return []
    terms = [
        line.strip()
        for line in denylist_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    findings: list[Finding] = []
    skip_parts = {".git", "apm_modules", "node_modules"}
    for md in sorted(root.rglob("*.md")):
        if skip_parts & set(md.parts) or not md.is_file():
            continue
        text = md.read_text(encoding="utf-8", errors="ignore").lower()
        for index, term in enumerate(terms, start=1):
            if term.lower() in text:
                findings.append(
                    Finding(
                        "error",
                        md,
                        f"contains privacy-denylisted term #{index} "
                        "(see local .privacy-denylist)",
                    )
                )
    return findings


def validate_skill_collection(skill_dirs: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    names: dict[str, Path] = {}

    for skill_dir in skill_dirs:
        findings.extend(validate_skill(skill_dir))
        findings.extend(validate_skill_length(skill_dir))
        try:
            frontmatter, _ = parse_skill(skill_dir / "SKILL.md")
        except PARSE_ERRORS:
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
        findings.extend(validate_privacy(root))

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

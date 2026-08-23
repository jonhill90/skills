#!/usr/bin/env python3
"""Mechanical checker for the loop-memory longitudinal scenario.

Compares dest/NN.json against a reference transform of src/NN.cfg for
every NN present in src/. Tells you PASS/FAIL/MISSING per file -- it does
NOT tell you why a file failed, matching TASK.md's own note. Correct
transform: drop blank lines and lines whose first non-whitespace
character is '#' (a full-line comment); every other line is `key = value`,
split on the FIRST '=' only, both sides stripped. A '#' that appears
mid-line, inside a value, is data, not a comment marker, and must survive
into the JSON value unchanged.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def reference_transform(cfg_path):
    result = {}
    for line in cfg_path.read_text().splitlines():
        if line.strip() == "":
            continue
        if line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def main():
    src_dir = HERE / "src"
    dest_dir = HERE / "dest"
    failures = 0
    total = 0
    for cfg_path in sorted(src_dir.glob("*.cfg")):
        total += 1
        n = cfg_path.stem
        expected = reference_transform(cfg_path)
        json_path = dest_dir / f"{n}.json"
        if not json_path.exists():
            print(f"{n}: MISSING")
            failures += 1
            continue
        try:
            actual = json.loads(json_path.read_text())
        except json.JSONDecodeError as e:
            print(f"{n}: FAIL (invalid JSON: {e})")
            failures += 1
            continue
        if actual == expected:
            print(f"{n}: PASS")
        else:
            print(f"{n}: FAIL (mismatch)")
            failures += 1
    print(f"\n{total - failures}/{total} passing")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

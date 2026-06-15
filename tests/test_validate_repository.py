from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate_repository.py"
SPEC = importlib.util.spec_from_file_location("validate_repository", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ValidateRepositoryTests(unittest.TestCase):
    def make_skill(
        self,
        root: Path,
        directory: str = "example-skill",
        frontmatter: str | None = None,
        body: str = "# Example\n\nRun the example.",
    ) -> Path:
        skill_dir = root / "skills" / directory
        skill_dir.mkdir(parents=True)
        metadata = frontmatter or (
            f"name: {directory}\n"
            "description: Run an example workflow. Use for validator tests."
        )
        (skill_dir / "SKILL.md").write_text(
            f"---\n{metadata}\n---\n\n{body}\n",
            encoding="utf-8",
        )
        return skill_dir

    def messages(self, findings: list[object]) -> list[str]:
        return [finding.message for finding in findings]

    def test_valid_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = self.make_skill(Path(temporary))
            self.assertEqual([], validator.validate_skill(skill_dir))

    def test_name_must_match_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = self.make_skill(
                Path(temporary),
                frontmatter=(
                    "name: different-name\n"
                    "description: Run an example workflow. Use for validator tests."
                ),
            )
            findings = validator.validate_skill(skill_dir)
            self.assertTrue(
                any("does not match directory" in message for message in self.messages(findings))
            )

    def test_unknown_frontmatter_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = self.make_skill(
                Path(temporary),
                frontmatter=(
                    "name: example-skill\n"
                    "description: Run an example workflow. Use for validator tests.\n"
                    "argument-hint: value"
                ),
            )
            findings = validator.validate_skill(skill_dir)
            self.assertIn(
                "non-portable frontmatter fields: argument-hint",
                self.messages(findings),
            )

    def test_broken_relative_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = self.make_skill(
                Path(temporary),
                body="# Example\n\nRead [missing](references/missing.md).",
            )
            findings = validator.validate_skill(skill_dir)
            self.assertIn(
                "relative link does not resolve: references/missing.md",
                self.messages(findings),
            )

    def test_script_must_be_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = self.make_skill(Path(temporary))
            script = skill_dir / "scripts" / "run.sh"
            script.parent.mkdir()
            script.write_text("#!/bin/sh\n", encoding="utf-8")
            os.chmod(script, 0o644)
            findings = validator.validate_skill(skill_dir)
            self.assertIn("script must have an executable mode", self.messages(findings))

    def test_duplicate_names_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = self.make_skill(root, directory="first")
            second = self.make_skill(
                root,
                directory="second",
                frontmatter=(
                    "name: first\n"
                    "description: Run another workflow. Use for duplicate tests."
                ),
            )
            findings = validator.validate_skill_collection([first, second])
            self.assertTrue(
                any("duplicate skill name" in message for message in self.messages(findings))
            )


if __name__ == "__main__":
    unittest.main()

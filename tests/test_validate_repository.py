from __future__ import annotations

import importlib.util
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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


class PrivacyDenylistTests(unittest.TestCase):
    def test_flags_denylisted_terms_in_tracked_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".privacy-denylist").write_text("AcmeCorp\nsecretproject\n")
            docs = root / "docs"; docs.mkdir()
            (docs / "note.md").write_text("mentions AcmeCorp storage\n")
            (docs / "clean.md").write_text("nothing to see\n")
            findings = validator.validate_privacy(root)
            self.assertEqual(len(findings), 1)
            self.assertIn("note.md", str(findings[0].path))
            # the term itself must not appear in the finding message
            self.assertNotIn("AcmeCorp", findings[0].message)

    def test_no_denylist_file_means_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(validator.validate_privacy(Path(td)), [])

    def test_broken_symlink_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".privacy-denylist").write_text("term\n")
            (root / "gone.md").symlink_to(root / "missing-target.md")
            self.assertEqual(validator.validate_privacy(root), [])


class FallbackFrontmatterTests(unittest.TestCase):
    def test_mini_yaml_matches_real_yaml_for_skill_frontmatter(self) -> None:
        import yaml as real_yaml

        text = (
            "name: my-skill\n"
            "description: Does things safely. Use when testing.\n"
            'license: "MIT"\n'
        )
        self.assertEqual(validator.mini_yaml(text), real_yaml.safe_load(text))
        # the fallback is deliberately more lenient than YAML: embedded
        # colons stay verbatim instead of raising
        self.assertEqual(
            validator.mini_yaml("description: a: b\n"), {"description": "a: b"}
        )

    def test_mini_yaml_strips_quotes_and_ignores_comments(self) -> None:
        parsed = validator.mini_yaml("# comment\nname: 'x'\n\ndescription: y\n")
        self.assertEqual(parsed, {"name": "x", "description": "y"})

    def test_invalid_skill_is_reported_without_pyyaml(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = Path(temporary) / "skills" / "bad-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("not frontmatter\n")
            with mock.patch.object(validator, "yaml", None):
                findings = validator.validate_skill(skill_dir)
            self.assertEqual(len(findings), 1)
            self.assertIn("must start with ---", findings[0].message)


class SkillLengthTests(unittest.TestCase):
    """AGENTS.md caps SKILL.md at 500 lines and nothing enforced it, so
    skills/tmux reached 493 unnoticed. A cap nothing checks is a
    convention."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skill = Path(self.tmp.name) / "demo"
        self.skill.mkdir()

    def _write(self, lines: int) -> Path:
        body = "---\nname: demo\ndescription: x\n---\n" + "\n".join(
            f"line {i}" for i in range(lines)
        )
        path = self.skill / "SKILL.md"
        path.write_text(body + "\n", encoding="utf-8")
        return path

    def test_over_the_cap_is_an_error(self) -> None:
        self._write(520)
        findings = validator.validate_skill_length(self.skill)
        self.assertTrue(findings)
        self.assertEqual(findings[0].level, "error")

    def test_approaching_the_cap_warns_early(self) -> None:
        """493 of 500 is seven lines from breaking and read as fine. A warning
        is what turns 'nobody noticed' into 'somebody was told'."""
        self._write(470)
        findings = validator.validate_skill_length(self.skill)
        self.assertTrue(findings)
        self.assertEqual(findings[0].level, "warning")

    def test_comfortably_short_is_silent(self) -> None:
        self._write(120)
        self.assertEqual(validator.validate_skill_length(self.skill), [])


class NoUnlabeledHarnessPathDependencyTests(unittest.TestCase):
    """Portable skill *behavior* cannot require a single harness's own
    config file to exist. Conditional compatibility guidance (a fallback
    documented alongside a stated harness label, e.g. tmux's `/loop`
    section) is fine; a bare instruction to read a Claude-only local
    override file is not — a Codex or Copilot agent following the skill
    has no such file to read. This scans the tree actually shipped, not a
    fixture, because the defect was content, not validator logic."""

    ROOT = Path(__file__).parents[1]

    # Vendor-owned local override/config file names that name exactly one
    # harness and have no cross-harness equivalent (unlike CLAUDE.md /
    # AGENTS.md, which are legitimate to name side by side as examples).
    FORBIDDEN_TOKENS = ("CLAUDE.local.md", "code.claude.com")

    def test_skills_do_not_hardcode_a_single_harness_config_path(self) -> None:
        offenders: list[str] = []
        for skill_md in sorted(self.ROOT.glob("skills/**/*.md")):
            text = skill_md.read_text(encoding="utf-8")
            for token in self.FORBIDDEN_TOKENS:
                if token in text:
                    offenders.append(f"{skill_md.relative_to(self.ROOT)}: {token}")
        self.assertEqual(offenders, [])

    def test_top_level_docs_do_not_link_a_single_vendor_spec_host(self) -> None:
        offenders: list[str] = []
        for doc in (self.ROOT / "README.md", self.ROOT / "AGENTS.md"):
            text = doc.read_text(encoding="utf-8")
            if "code.claude.com" in text:
                offenders.append(doc.name)
        self.assertEqual(offenders, [])


class NoDanglingEvalReferenceTests(unittest.TestCase):
    """jonhill90/skills#128: behavioral scenarios, counter-scenarios,
    harness runners, results, transcripts, and scoring/arming tools moved
    to the private jonhill90/agent-evals repository. A skill that points a
    reader at private evidence without saying so is a broken instruction,
    and it leaks the shape of private material. This scans the tree
    actually shipped (SKILL.md, references/, scripts/) so the class cannot
    silently reappear — the content, not validator logic, is the risk."""

    ROOT = Path(__file__).parents[1]

    # Identifiers with no plausible portable meaning outside the private
    # eval suite; a hard ban wherever they show up in skill content.
    HARD_BANNED = ("eval_arm", "EVAL_ARM", "tests/evals")
    E_ID_RE = re.compile(r"(?<![\w/-])E(?:[1-9]|1[0-9]|20)(?![\w-])")
    LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

    # A plain-text mention of the private repo is allowed (AGENTS.md:
    # "plain provenance statements ... are fine"), but only paired with an
    # explicit statement that the evidence isn't public.
    UNAVAILABLE_PHRASES = (
        "not publicly available",
        "not published here",
        "private evaluation",
    )

    # A dated citation shaped "(YYYY-MM-DD, <label> run)" points at a
    # specific private eval run without naming agent-evals or using a link
    # — the string- and link-based checks above don't key on it. Scoped
    # tightly to that parenthetical shape (date, comma, the word "run", no
    # nested parens) so it doesn't fire on unrelated dated prose elsewhere
    # in the tree.
    DATED_RUN_RE = re.compile(
        r"\(([^()]*\d{4}-\d{2}-\d{2}(?:/\d{2})?[^()]*\brun\b[^()]*)\)",
        re.DOTALL,
    )

    def _skill_files(self) -> list[Path]:
        paths = set(self.ROOT.glob("skills/**/SKILL.md"))
        paths |= set(self.ROOT.glob("skills/**/references/**/*"))
        paths |= set(self.ROOT.glob("skills/**/scripts/**/*"))
        return sorted(path for path in paths if path.is_file())

    def test_no_hard_banned_eval_identifiers(self) -> None:
        offenders: list[str] = []
        for path in self._skill_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in self.HARD_BANNED:
                if token in text:
                    offenders.append(f"{path.relative_to(self.ROOT)}: {token!r}")
            for match in self.E_ID_RE.finditer(text):
                offenders.append(
                    f"{path.relative_to(self.ROOT)}: scenario identifier {match.group(0)!r}"
                )
        self.assertEqual(offenders, [])

    def test_no_clickable_link_to_private_agent_evals_repo(self) -> None:
        offenders: list[str] = []
        for path in self._skill_files():
            if path.suffix != ".md":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in self.LINK_RE.finditer(text):
                if "agent-evals" in match.group(1).lower():
                    offenders.append(f"{path.relative_to(self.ROOT)}: {match.group(0)}")
        self.assertEqual(offenders, [])

    def test_agent_evals_mentions_state_evidence_is_not_public(self) -> None:
        offenders: list[str] = []
        for path in self._skill_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "agent-evals" not in text.lower():
                continue
            if not any(phrase in text.lower() for phrase in self.UNAVAILABLE_PHRASES):
                offenders.append(str(path.relative_to(self.ROOT)))
        self.assertEqual(offenders, [])

    def test_dated_run_citation_discloses_private_evidence(self) -> None:
        offenders: list[str] = []
        for path in self._skill_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in self.DATED_RUN_RE.finditer(text):
                # Collapse line wraps so a phrase split across a hard-wrapped
                # line (e.g. "not\n  publicly available") still matches.
                clause = " ".join(match.group(1).lower().split())
                if "agent-evals" not in clause:
                    offenders.append(
                        f"{path.relative_to(self.ROOT)}: "
                        f"{match.group(0)!r} names a run but not agent-evals"
                    )
                    continue
                if not any(phrase in clause for phrase in self.UNAVAILABLE_PHRASES):
                    offenders.append(
                        f"{path.relative_to(self.ROOT)}: "
                        f"{match.group(0)!r} names agent-evals but doesn't say it's private"
                    )
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()

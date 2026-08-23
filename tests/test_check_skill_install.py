"""jonhill90/skills#230: mutation-check for check_skill_install.py's own
three-way verdict (OK / MISSING / DIVERGENT) -- see that module's own
doc comment for why this exists and why the two failure states must
stay distinct rather than collapsing into one "bad install" message.

Every fixture here is synthetic and self-contained (tmp dirs built per
test), not this machine's own real ~/.claude/skills/ state -- the real
machine's own two live failures (a genuinely missing skill and a
genuinely divergent one, found while building this) are demonstrated in
the PR body instead, per this task's own instruction that a synthetic
unit test alone is not enough evidence; this file's job is the
mechanical guarantee (every state, every edge case, every time, in CI),
not the live proof.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_skill_install as csi  # noqa: E402


def _write_repo_skill(repo_root: Path, name: str, files: dict[str, str]) -> Path:
    """repo_root/skills/<name>/... -- this repo's own on-disk shape."""
    return _write_files(repo_root / "skills" / name, files)


def _write_installed_skill(claude_skills_dir: Path, name: str, files: dict[str, str]) -> Path:
    """claude_skills_dir/<name>/... -- ~/.claude/skills' own shape, no
    intermediate "skills/" segment (that is only this repo's own layout,
    not the shared skills path's)."""
    return _write_files(claude_skills_dir / name, files)


def _write_files(skill_dir: Path, files: dict[str, str]) -> Path:
    for rel, content in files.items():
        path = skill_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return skill_dir


class CheckInstalledTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo_root = self.tmp / "repo"
        self.claude_skills_dir = self.tmp / "claude-skills"
        self.claude_skills_dir.mkdir(parents=True)

    def test_matching_copy_is_ok(self):
        files = {"SKILL.md": "---\nname: foo\n---\nbody\n"}
        _write_repo_skill(self.repo_root, "foo", files)
        _write_installed_skill(self.tmp / "claude-skills-src", "foo", files)
        installed = self.claude_skills_dir / "foo"
        installed.parent.mkdir(parents=True, exist_ok=True)
        installed.symlink_to(self.tmp / "claude-skills-src" / "foo")

        result = csi.check_installed("foo", self.claude_skills_dir, self.repo_root)
        self.assertEqual(result.status, csi.OK)
        self.assertEqual(result.exit_code, csi.EXIT_OK)
        self.assertEqual(result.only_in_repo, [])
        self.assertEqual(result.only_in_installed, [])
        self.assertEqual(result.differing, [])

    def test_matching_real_copy_not_a_symlink_is_also_ok(self):
        """A real (non-symlinked) copy that happens to match byte-for-byte
        is OK too -- the check compares content, not installation
        mechanism. Matters because this repo's own skills are installed
        both ways on the real machine (most symlinked, a few as plain
        copied directories)."""
        files = {"SKILL.md": "---\nname: bar\n---\nbody\n"}
        _write_repo_skill(self.repo_root, "bar", files)
        _write_installed_skill(self.claude_skills_dir, "bar", files)

        result = csi.check_installed("bar", self.claude_skills_dir, self.repo_root)
        self.assertEqual(result.status, csi.OK)

    def test_missing_skill_is_reported_missing_not_divergent(self):
        _write_repo_skill(self.repo_root, "gone", {"SKILL.md": "x\n"})
        # Deliberately never create claude_skills_dir/gone at all.

        result = csi.check_installed("gone", self.claude_skills_dir, self.repo_root)
        self.assertEqual(result.status, csi.MISSING)
        self.assertEqual(result.exit_code, csi.EXIT_MISSING)
        self.assertIn("MISSING", result.message)
        self.assertIn(str(self.claude_skills_dir / "gone"), result.message)

    def test_dangling_symlink_is_missing_not_divergent(self):
        """A symlink pointing at nothing is not installed in any sense
        this check cares about -- must read as MISSING, the same as no
        symlink at all, not as a comparison against an empty tree."""
        _write_repo_skill(self.repo_root, "dangling", {"SKILL.md": "x\n"})
        (self.claude_skills_dir / "dangling").symlink_to(self.tmp / "nowhere")

        result = csi.check_installed("dangling", self.claude_skills_dir, self.repo_root)
        self.assertEqual(result.status, csi.MISSING)

    def test_divergent_content_is_named_specifically(self):
        _write_repo_skill(self.repo_root, "drifted", {"SKILL.md": "repo version\n"})
        _write_installed_skill(self.claude_skills_dir, "drifted", {"SKILL.md": "installed version\n"})

        result = csi.check_installed("drifted", self.claude_skills_dir, self.repo_root)
        self.assertEqual(result.status, csi.DIVERGENT)
        self.assertEqual(result.exit_code, csi.EXIT_DIVERGENT)
        self.assertEqual(result.differing, ["SKILL.md"])
        self.assertEqual(result.only_in_repo, [])
        self.assertEqual(result.only_in_installed, [])

    def test_divergent_missing_file_is_named_specifically(self):
        """The repo shipped a new file (e.g. an eval-scenario/) the
        installed copy never picked up -- distinct from a content diff on
        a shared file, and reported as its own list."""
        _write_repo_skill(self.repo_root, "stale", {
            "SKILL.md": "same\n",
            "references/new-thing.md": "added later\n",
        })
        _write_installed_skill(self.claude_skills_dir, "stale", {"SKILL.md": "same\n"})

        result = csi.check_installed("stale", self.claude_skills_dir, self.repo_root)
        self.assertEqual(result.status, csi.DIVERGENT)
        self.assertEqual(result.only_in_repo, ["references/new-thing.md"])
        self.assertEqual(result.differing, [])

    def test_divergent_extra_file_is_named_specifically(self):
        """The installed copy has a file the repo's own current version
        doesn't -- e.g. a leftover from an older layout -- reported
        separately from "missing" and from a content diff."""
        _write_repo_skill(self.repo_root, "leftover", {"SKILL.md": "same\n"})
        _write_installed_skill(self.claude_skills_dir, "leftover", {
            "SKILL.md": "same\n",
            "old-file.md": "should have been removed\n",
        })

        result = csi.check_installed("leftover", self.claude_skills_dir, self.repo_root)
        self.assertEqual(result.status, csi.DIVERGENT)
        self.assertEqual(result.only_in_installed, ["old-file.md"])
        self.assertEqual(result.differing, [])

    def test_unknown_skill_raises_rather_than_reporting_a_state(self):
        """Checking a name with no skills/<name>/ directory in the repo at
        all is a caller error, not an install-state finding -- must not
        silently report MISSING for a typo the same way it would for a
        real skill genuinely not installed."""
        with self.assertRaises(ValueError):
            csi.check_installed("not-a-real-skill", self.claude_skills_dir, self.repo_root)


class MainCLITests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo_root = self.tmp / "repo"
        self.claude_skills_dir = self.tmp / "claude-skills"
        self.claude_skills_dir.mkdir(parents=True)

    def test_cli_exit_code_ok(self):
        files = {"SKILL.md": "x\n"}
        _write_repo_skill(self.repo_root, "cli-ok", files)
        _write_installed_skill(self.claude_skills_dir, "cli-ok", files)
        code = csi.main([
            "cli-ok",
            "--claude-skills-dir", str(self.claude_skills_dir),
            "--repo-root", str(self.repo_root),
        ])
        self.assertEqual(code, csi.EXIT_OK)

    def test_cli_exit_code_missing(self):
        _write_repo_skill(self.repo_root, "cli-missing", {"SKILL.md": "x\n"})
        code = csi.main([
            "cli-missing",
            "--claude-skills-dir", str(self.claude_skills_dir),
            "--repo-root", str(self.repo_root),
        ])
        self.assertEqual(code, csi.EXIT_MISSING)

    def test_cli_exit_code_divergent(self):
        _write_repo_skill(self.repo_root, "cli-divergent", {"SKILL.md": "a\n"})
        _write_installed_skill(self.claude_skills_dir, "cli-divergent", {"SKILL.md": "b\n"})
        code = csi.main([
            "cli-divergent",
            "--claude-skills-dir", str(self.claude_skills_dir),
            "--repo-root", str(self.repo_root),
        ])
        self.assertEqual(code, csi.EXIT_DIVERGENT)

    def test_cli_exit_code_unknown_skill(self):
        code = csi.main([
            "totally-not-a-skill",
            "--claude-skills-dir", str(self.claude_skills_dir),
            "--repo-root", str(self.repo_root),
        ])
        self.assertEqual(code, csi.EXIT_COULD_NOT_CHECK)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "skills" / "organize-repository" / "scripts" / "check_layout.py"
SPEC = importlib.util.spec_from_file_location("check_layout", SCRIPT_PATH)
assert SPEC and SPEC.loader
check_layout = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_layout
SPEC.loader.exec_module(check_layout)


class LayoutFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.root = Path(self.tmpdir.name)
        self.write("README.md", "# project\n")
        self.write("AGENTS.md", "# agents\n")

    def write(self, rel: str, text: str = "") -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def rules(self, severity: str | None = None) -> list[str]:
        return [
            f.rule
            for f in check_layout.check(self.root)
            if severity is None or f.severity == severity
        ]


class EntryPointTests(LayoutFixture):
    def test_clean_repository_has_no_findings(self) -> None:
        self.assertEqual(self.rules(), [])

    def test_missing_readme_is_an_error(self) -> None:
        (self.root / "README.md").unlink()
        self.assertIn("entry-point", self.rules("error"))

    def test_missing_agents_md_is_a_warning(self) -> None:
        (self.root / "AGENTS.md").unlink()
        self.assertIn("entry-point", self.rules("warning"))


class InstructionFileTests(LayoutFixture):
    def test_claude_md_symlink_to_agents_md_is_fine(self) -> None:
        os.symlink("AGENTS.md", self.root / "CLAUDE.md")
        self.assertEqual(self.rules(), [])

    def test_claude_md_importing_agents_md_is_fine(self) -> None:
        self.write("CLAUDE.md", "@AGENTS.md\n\n## Claude only\n")
        self.assertEqual(self.rules(), [])

    def test_agents_md_symlink_to_claude_md_is_inverted(self) -> None:
        (self.root / "AGENTS.md").unlink()
        self.write("CLAUDE.md", "# rules\n")
        os.symlink("CLAUDE.md", self.root / "AGENTS.md")
        self.assertIn("instruction-file", self.rules("warning"))

    def test_two_independent_instruction_files_can_drift(self) -> None:
        self.write("CLAUDE.md", "# separate rules\n")
        self.assertIn("instruction-file", self.rules("warning"))


class PlaceholderTests(LayoutFixture):
    def test_directory_holding_only_gitkeep_is_a_placeholder(self) -> None:
        self.write("docs/runbooks/.gitkeep")
        self.assertIn("placeholder-dir", self.rules("warning"))

    def test_directory_with_content_is_not_a_placeholder(self) -> None:
        self.write("docs/runbooks/.gitkeep")
        self.write("docs/runbooks/rotate-token.md", "# rotate\n")
        self.assertNotIn("placeholder-dir", self.rules())


class PytestBasenameTests(LayoutFixture):
    """Measured 2026-09-29 with pytest 9.1.1: mirrored tests/<feature>/test_x.py
    files without __init__.py fail collection under the default prepend mode."""

    def setUp(self) -> None:
        super().setUp()
        self.write("pyproject.toml", '[project]\nname = "app"\n')
        self.write("tests/conftest.py")
        self.write("tests/accounts/test_service.py")
        self.write("tests/billing/test_service.py")

    def test_duplicate_basenames_without_packages_is_an_error(self) -> None:
        self.assertIn("pytest-basename", self.rules("error"))

    def test_collision_is_caught_when_nothing_mentions_pytest(self) -> None:
        # The measured failing fixture: pytest installed into a venv, no
        # conftest.py, and no pytest reference in any config file.
        (self.root / "tests/conftest.py").unlink()
        self.assertIn("pytest-basename", self.rules("error"))

    def test_importlib_mode_in_pyproject_fixes_it(self) -> None:
        self.write(
            "pyproject.toml",
            '[project]\nname = "app"\n\n[tool.pytest.ini_options]\naddopts = "--import-mode=importlib"\n',
        )
        self.assertNotIn("pytest-basename", self.rules())

    def test_init_files_make_the_names_unique(self) -> None:
        self.write("tests/__init__.py")
        self.write("tests/accounts/__init__.py")
        self.write("tests/billing/__init__.py")
        self.assertNotIn("pytest-basename", self.rules())

    def test_repeated_conftest_is_not_flagged(self) -> None:
        self.write("tests/accounts/test_service.py", "")
        (self.root / "tests/billing/test_service.py").rename(self.root / "tests/billing/test_billing.py")
        self.write("tests/accounts/conftest.py")
        self.assertNotIn("pytest-basename", self.rules())

    def test_virtualenv_contents_are_ignored(self) -> None:
        (self.root / "tests/billing/test_service.py").unlink()
        self.write(".venv/lib/site-packages/pkg/tests/test_service.py")
        self.assertNotIn("pytest-basename", self.rules())


class MintlifyTests(LayoutFixture):
    """Measured 2026-09-29 with `mint dev`: pages missing from navigation are
    still served by URL unless .mintignore excludes them; README.md is not."""

    def setUp(self) -> None:
        super().setUp()
        self.write(
            "docs/docs.json",
            json.dumps(
                {
                    "name": "Test",
                    "navigation": {
                        "groups": [
                            {"group": "Start", "pages": ["index", {"group": "Guides", "pages": ["guides/refunds"]}]}
                        ]
                    },
                }
            ),
        )
        self.write("docs/index.mdx", "hello\n")
        self.write("docs/guides/refunds.mdx", "guide\n")
        self.write("docs/README.md", "# docs index\n")

    def exposed(self) -> list[str]:
        return sorted(
            str(f.path.relative_to(self.root))
            for f in check_layout.check(self.root)
            if f.rule == "mintlify-exposed"
        )

    def test_site_with_only_navigated_pages_is_clean(self) -> None:
        self.assertEqual(self.exposed(), [])

    def test_maintainer_doc_outside_navigation_is_exposed(self) -> None:
        self.write("docs/runbooks/rotate.md", "# internal\n")
        self.write("docs/architecture.md", "# internal\n")
        self.assertEqual(self.exposed(), ["docs/architecture.md", "docs/runbooks/rotate.md"])

    def test_denylist_mintignore_covers_only_what_it_names(self) -> None:
        self.write("docs/.mintignore", "decisions/\n")
        self.write("docs/decisions/0001-flat.md", "# adr\n")
        self.write("docs/runbooks/rotate.md", "# internal\n")
        self.assertEqual(self.exposed(), ["docs/runbooks/rotate.md"])

    def test_allowlist_mintignore_hides_everything_unlisted(self) -> None:
        self.write("docs/.mintignore", "/*\n!/docs.json\n!/index.mdx\n!/guides/\n")
        self.write("docs/decisions/0001-flat.md", "# adr\n")
        self.write("docs/runbooks/rotate.md", "# internal\n")
        self.write("docs/architecture.md", "# internal\n")
        self.assertEqual(self.exposed(), [])

    def test_allowlist_still_exposes_unlisted_page_inside_published_folder(self) -> None:
        self.write("docs/.mintignore", "/*\n!/docs.json\n!/index.mdx\n!/guides/\n")
        self.write("docs/guides/draft.mdx", "draft\n")
        self.assertEqual(self.exposed(), ["docs/guides/draft.mdx"])

    def test_json_file_without_navigation_is_not_a_mintlify_root(self) -> None:
        self.write("config/docs.json", json.dumps({"unrelated": True}))
        self.write("config/notes.md", "# notes\n")
        self.assertEqual(self.exposed(), [])


class CommandLineTests(LayoutFixture):
    def run_main(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_layout.main([str(self.root), *args])
        return code, out.getvalue()

    def test_clean_repository_exits_zero(self) -> None:
        code, out = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("0 error(s), 0 warning(s)", out)

    def test_warnings_alone_exit_zero(self) -> None:
        self.write("docs/runbooks/.gitkeep")
        code, _ = self.run_main()
        self.assertEqual(code, 0)

    def test_errors_exit_one(self) -> None:
        (self.root / "README.md").unlink()
        code, _ = self.run_main()
        self.assertEqual(code, 1)

    def test_missing_root_exits_two(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_layout.main([str(self.root / "missing")])
        self.assertEqual(code, 2)

    def test_json_output_lists_findings(self) -> None:
        self.write("docs/runbooks/.gitkeep")
        code, out = self.run_main("--json")
        self.assertEqual(code, 0)
        findings = json.loads(out)
        self.assertEqual([f["rule"] for f in findings], ["placeholder-dir"])
        self.assertEqual(findings[0]["path"], "docs/runbooks")


if __name__ == "__main__":
    unittest.main()

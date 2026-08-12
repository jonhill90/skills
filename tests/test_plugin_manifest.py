"""Guard `plugin.json` against drift from Agent Plugins 1.0.0.

The manifest is two required fields and a closed schema, which makes it
exactly the kind of file that is written once, never looked at again, and
silently invalidated by a well-meant hand edit. `additionalProperties` is
`false` in the published schema, so a single extra or misspelled key is a
hard validation failure for every conformant client, not a warning
(jonhill90/skills#159).

These checks run OFFLINE and encode the spec's constraints as this
repository reads them. That is deliberately not the whole story: reading a
spec and comparing it to your own code is the same author checking their own
work, which is why the `plugin-conformance` CI job validates this same file
against the PUBLISHED schema fetched from agent-plugins.org. This module is
the fast local guard; that job is the independent instrument. Both, for the
same reason `spec-conformance` exists alongside `validate_repository.py`.

Constraints below are transcribed from
https://agent-plugins.org/schemas/1.0.0/plugin.schema.json (fetched
2026-08-12) and https://agent-plugins.org/specification.
"""

from __future__ import annotations

import json
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# "Clients MUST check for a manifest at `plugin.json` in the plugin root."
MANIFEST_PATH = ROOT / "plugin.json"

SCHEMA_URL = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"

# "Its schema is closed: the only permitted top-level fields are `$schema`,
# `name`, `version`, `description`, `author`, `homepage`, `repository`,
# `license`, `keywords`, and `extensions`."
ALLOWED_TOP_LEVEL = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
REQUIRED_TOP_LEVEL = {"$schema", "name"}

# The schema's own `name` pattern, verbatim. The negative lookahead is what
# rejects consecutive separators (`a--b`, `a..b`); the anchors are what
# require an alphanumeric first and last character.
NAME_PATTERN = r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$"

# `author` is an object with its own closed schema.
ALLOWED_AUTHOR_KEYS = {"name", "email", "url"}

STRING_FIELDS = ("name", "version", "description", "homepage", "repository", "license")


class PluginManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = MANIFEST_PATH.read_text(encoding="utf-8")
        cls.manifest = json.loads(cls.raw)

    def test_manifest_exists_at_the_plugin_root(self):
        # Not `.claude-plugin/plugin.json`, not `docs/`: the spec names one
        # location and clients only check that one.
        self.assertTrue(MANIFEST_PATH.is_file(), f"{MANIFEST_PATH} is missing")
        self.assertEqual(MANIFEST_PATH.parent, ROOT)

    def test_manifest_is_a_json_object(self):
        self.assertIsInstance(self.manifest, dict)

    def test_schema_field_is_the_exact_published_url(self):
        # A `const` in the schema: near-misses (http://, a 1.0 path, a
        # trailing slash) are failures, not approximations.
        self.assertEqual(self.manifest.get("$schema"), SCHEMA_URL)

    def test_required_fields_are_present(self):
        self.assertTrue(REQUIRED_TOP_LEVEL.issubset(self.manifest))

    def test_no_field_outside_the_closed_schema(self):
        extra = sorted(set(self.manifest) - ALLOWED_TOP_LEVEL)
        self.assertEqual(extra, [], f"closed schema: these keys are not permitted: {extra}")

    def test_name_matches_the_specs_pattern(self):
        name = self.manifest["name"]
        self.assertIsInstance(name, str)
        self.assertTrue(1 <= len(name) <= 64, f"name must be 1-64 chars, got {len(name)}")
        self.assertRegex(name, NAME_PATTERN)

    def test_name_pattern_rejects_what_the_spec_says_it_rejects(self):
        # The pattern is the load-bearing part of this file; a pattern that
        # accepts everything would make the test above vacuous.
        compiled = re.compile(NAME_PATTERN)
        for bad in ("Skills", "-skills", "skills-", "jon--hill", "a..b", "skills_repo", "", "a b"):
            self.assertIsNone(compiled.match(bad), f"{bad!r} should not be a valid plugin name")
        for good in ("jonhill90-skills", "a", "skills.core", "a1"):
            self.assertIsNotNone(compiled.match(good), f"{good!r} should be a valid plugin name")

    def test_author_object_stays_within_its_own_closed_schema(self):
        author = self.manifest.get("author")
        if author is None:
            return
        self.assertIsInstance(author, dict)
        extra = sorted(set(author) - ALLOWED_AUTHOR_KEYS)
        self.assertEqual(extra, [], f"author keys not permitted: {extra}")

    def test_optional_fields_have_the_right_types(self):
        for field in STRING_FIELDS:
            if field in self.manifest:
                self.assertIsInstance(self.manifest[field], str, f"{field} must be a string")
        if "keywords" in self.manifest:
            self.assertIsInstance(self.manifest["keywords"], list)
            for keyword in self.manifest["keywords"]:
                self.assertIsInstance(keyword, str)

    def test_manifest_declares_no_license_this_repository_does_not_carry(self):
        # There is no LICENSE file in this tree. A `license` field would be a
        # claim the repository cannot back, which is worse than its absence.
        if "license" in self.manifest:
            self.assertTrue(
                any((ROOT / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt")),
                "plugin.json declares a license but no LICENSE file exists",
            )


class PluginLayoutTests(unittest.TestCase):
    """The parts of the spec that are about the tree, not the manifest."""

    def test_every_skill_matches_the_discovery_convention(self):
        # "Each immediate child directory containing a path named exactly
        # `SKILL.md` that resolves to a regular file is treated as one skill."
        skills_dir = ROOT / "skills"
        self.assertTrue(skills_dir.is_dir())
        discovered = [d for d in sorted(skills_dir.iterdir()) if d.is_dir() and (d / "SKILL.md").is_file()]
        self.assertEqual(
            [d.name for d in discovered],
            [d.name for d in sorted(skills_dir.iterdir()) if d.is_dir()],
            "every directory under skills/ must hold a SKILL.md or a client will silently skip it",
        )
        self.assertGreater(len(discovered), 0)

    def test_no_tracked_path_resolves_outside_the_plugin_root(self):
        # "When a client discovers, reads, or executes a file or directory
        # supplied by the plugin package, the filesystem-resolved path MUST
        # remain within the filesystem-resolved plugin root." This repository
        # ships symlinks on purpose (CLAUDE.md and the Copilot instructions
        # both point at AGENTS.md), so the check is that they stay inside,
        # not that they do not exist.
        root = os.path.realpath(ROOT)
        escaping = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            if ".git" in dirnames:
                dirnames.remove(".git")
            for name in dirnames + filenames:
                path = Path(dirpath) / name
                if not path.is_symlink():
                    continue
                resolved = os.path.realpath(path)
                if os.path.commonpath([resolved, root]) != root:
                    escaping.append(f"{path} -> {resolved}")
        self.assertEqual(escaping, [], f"symlinks escaping the plugin root: {escaping}")


if __name__ == "__main__":
    unittest.main()

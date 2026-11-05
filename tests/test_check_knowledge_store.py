from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "organize-repository"
    / "scripts"
    / "check_knowledge_store.py"
)
SPEC = importlib.util.spec_from_file_location("check_knowledge_store", SCRIPT_PATH)
assert SPEC and SPEC.loader
cks = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cks
SPEC.loader.exec_module(cks)

# A small store that passes every check: each hub links its children with a
# description, the one note is linked from an area map, and nothing is copied.
CLEAN_STORE = {
    "README.md": (
        "# Store\n\n"
        "Before saving, run the wizard in 99-meta/ORGANIZE.md; to find anything, "
        "follow the hub lists from here.\n\n"
        "- [01-notes](01-notes/README.md): notes we wrote ourselves\n"
        "- [03-areas](03-areas/README.md): subjects that never end\n"
        "- [99-meta](99-meta/README.md): how this store works\n"
    ),
    "01-notes/README.md": "# Notes\n\n- [01a-atomic](01a-atomic/README.md): one idea per note\n",
    "01-notes/01a-atomic/README.md": (
        "# Atomic\n\n- [joining-network](joining-network.md): how an agent joins the network\n"
    ),
    "01-notes/01a-atomic/joining-network.md": (
        "---\ntitle: Joining the network\ndescription: How an agent joins the network\n"
        "status: current\ndate: 2026-11-03\n---\n\n# Joining the network\n"
    ),
    "03-areas/README.md": "# Areas\n\n- [networking](networking.md): the private network map\n",
    "03-areas/networking.md": (
        "# Networking\n\n- [Joining](../01-notes/01a-atomic/joining-network.md): first step for any agent\n"
    ),
    "99-meta/README.md": "# Meta\n\n- [ORGANIZE](ORGANIZE.md): the wizard and naming rule\n",
    "99-meta/ORGANIZE.md": "# Organization standard\n\nThe wizard lives here.\n",
}


class StoreFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.root = Path(self.tmpdir.name)
        for rel, text in CLEAN_STORE.items():
            self.write(rel, text)

    def write(self, rel: str, text: str = "x\n") -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def checks(self) -> list[str]:
        return [c for c, _, _ in cks.check(str(self.root))]

    def faults(self) -> list[tuple[str, str, str]]:
        return cks.check(str(self.root))

    def run_main(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = cks.main(list(args))
        return code, out.getvalue()


class CleanStoreTests(StoreFixture):
    def test_clean_store_has_no_faults(self) -> None:
        self.assertEqual(self.faults(), [])

    def test_main_exits_zero_on_a_clean_store(self) -> None:
        self.assertEqual(self.run_main(str(self.root))[0], 0)

    def test_main_exits_two_on_bad_input(self) -> None:
        self.assertEqual(self.run_main(str(self.root / "missing"))[0], 2)


class RootTests(StoreFixture):
    def test_unknown_top_folder_fails(self) -> None:
        self.write("stuff/note.md")
        self.assertIn("root", self.checks())

    def test_loose_file_at_root_fails(self) -> None:
        self.write("notes.md")
        self.assertIn("root", self.checks())

    def test_role_files_and_dot_files_at_root_pass(self) -> None:
        self.write("AGENTS.md", "# agents\n")
        self.write(".gitignore", "*.tmp\n")
        self.assertNotIn("root", self.checks())


class NameTests(unittest.TestCase):
    def faults(self, rel: str, is_dir: bool = False) -> list[str]:
        return [why for _, why in cks.name_faults(rel, is_dir)]

    def test_kebab_name_passes(self) -> None:
        self.assertEqual(self.faults("01-notes/01a-atomic/joining-network.md"), [])

    def test_capitals_fail_outside_role_files(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/Joining-Network.md"))

    def test_role_file_capitals_pass(self) -> None:
        self.assertEqual(self.faults("01-notes/01r-research/0107-graphs/SYNTHESIS.md"), [])

    def test_date_in_name_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/plan-2026-11-03.md"))

    def test_id_token_in_name_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/bl-0166-skill.md"))

    def test_version_suffix_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/plan-v2.md"))

    def test_catch_all_word_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/misc.md"))

    def test_batch_number_allowed_only_in_research(self) -> None:
        self.assertEqual(self.faults("01-notes/01r-research/0107-graphs", True), [])
        self.assertTrue(self.faults("01-notes/01a-atomic/0107-graphs", True))

    def test_lettered_folder_must_carry_parent_number(self) -> None:
        self.assertTrue(self.faults("01-notes/04p-pages", True))
        self.assertTrue(self.faults("01-notes/atomic", True))

    def test_area_is_a_file_not_a_folder(self) -> None:
        self.assertTrue(self.faults("03-areas/networking", True))

    def test_snake_case_python_passes(self) -> None:
        self.assertEqual(self.faults("99-meta/tools/check_store.py"), [])

    def test_name_repeating_a_parent_folder_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01r-research/graphs/graphs", True))

    def test_windows_device_name_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/con.md"))

    def test_captured_material_keeps_its_names(self) -> None:
        self.assertEqual(self.faults("04-resources/04r-repos/some-repo/Makefile"), [])
        self.assertEqual(self.faults("01-notes/01r-research/graphs/sources/Paper_2024.pdf"), [])


class LinkAndOrphanTests(StoreFixture):
    def test_dead_link_fails(self) -> None:
        self.write("03-areas/networking.md", "# Networking\n\n- [Gone](../01-notes/01a-atomic/gone.md): dead\n")
        self.assertIn("links", self.checks())

    def test_links_inside_code_are_ignored(self) -> None:
        self.write(
            "01-notes/01a-atomic/joining-network.md",
            "# Joining\n\n`[x](nowhere.md)`\n\n```\n[y](nowhere.md)\n```\n",
        )
        self.assertNotIn("links", self.checks())

    def test_unlinked_file_is_an_orphan(self) -> None:
        self.write("01-notes/01a-atomic/lonely.md", "# Lonely\n")
        self.assertIn("orphans", self.checks())

    def test_files_inside_a_linked_item_folder_are_reached(self) -> None:
        self.write("01-notes/01a-atomic/joining-network.md", "")
        (self.root / "01-notes/01a-atomic/joining-network.md").unlink()
        self.write("01-notes/01a-atomic/joining-network/README.md", "# Joining\n")
        self.write("01-notes/01a-atomic/joining-network/data/hosts.csv", "a,b\n")
        self.write(
            "01-notes/01a-atomic/README.md",
            "# Atomic\n\n- [joining-network](joining-network/): how an agent joins the network\n",
        )
        self.write(
            "03-areas/networking.md",
            "# Networking\n\n- [Joining](../01-notes/01a-atomic/joining-network/): first step\n",
        )
        self.assertEqual(self.faults(), [])


class TwinTests(StoreFixture):
    def test_two_files_with_the_same_bytes_fail(self) -> None:
        self.write("01-notes/01a-atomic/copy-of-note.md", CLEAN_STORE["01-notes/01a-atomic/joining-network.md"])
        self.assertIn("twins", self.checks())

    def test_captured_copies_are_not_twins(self) -> None:
        self.write("04-resources/04p-pages/page-one/sources/a.html", "same\n")
        self.write("04-resources/04p-pages/page-one/sources/b.html", "same\n")
        self.assertNotIn("twins", self.checks())


class HubTests(StoreFixture):
    def test_hub_missing_a_child_fails(self) -> None:
        self.write("01-notes/01a-atomic/second-note.md", "# Second\n")
        self.assertIn("hubs", self.checks())

    def test_hub_line_without_description_fails(self) -> None:
        self.write("03-areas/README.md", "# Areas\n\n- [networking](networking.md)\n")
        self.assertIn("hubs", self.checks())

    def test_missing_hub_readme_fails(self) -> None:
        (self.root / "99-meta/README.md").unlink()
        self.assertIn("hubs", self.checks())

    def test_hubs_flag_prints_the_missing_line(self) -> None:
        self.write(
            "01-notes/01a-atomic/second-note.md",
            "---\ndescription: The second idea\n---\n# Second\n",
        )
        code, out = self.run_main(str(self.root), "--hubs")
        self.assertEqual(code, 0)
        self.assertIn("[second-note.md](second-note.md): The second idea", out)


class MapTests(StoreFixture):
    def test_item_without_a_map_link_fails(self) -> None:
        self.write("03-areas/networking.md", "# Networking\n\nNo links yet.\n")
        self.assertIn("maps", self.checks())

    def test_project_folder_needs_its_map_note(self) -> None:
        self.write("02-projects/README.md", "# Projects\n\n- [move](move/plan.md): the move plan\n")
        self.write("02-projects/move/plan.md", "# Plan\n")
        self.write(
            "README.md",
            CLEAN_STORE["README.md"] + "- [02-projects](02-projects/README.md): work that will end\n",
        )
        rows = [(c, p) for c, p, _ in self.faults() if c == "maps"]
        self.assertIn(("maps", "02-projects/move/"), rows)

    def test_project_folder_has_no_readme(self) -> None:
        self.write("02-projects/README.md", "# Projects\n\n- [move](move.md): moving the store\n")
        self.write("02-projects/move.md", "# Move\n\n- [plan](move/plan.md): the steps in order\n")
        self.write("02-projects/move/plan.md", "# Plan\n")
        self.write("02-projects/move/README.md", "# Move\n")
        rows = [p for c, p, _ in self.faults() if c == "maps"]
        self.assertIn("02-projects/move/README.md", rows)


class PathAndFindTests(StoreFixture):
    def test_path_mode_checks_a_proposed_name(self) -> None:
        self.assertEqual(self.run_main(str(self.root), "--path", "01-notes/01a-atomic/good-name.md")[0], 0)
        code, out = self.run_main(str(self.root), "--path", "01-notes/01a-atomic/Bad Name.md")
        self.assertEqual(code, 1)
        self.assertIn("FAIL names", out)

    def test_find_returns_the_store_root(self) -> None:
        found = cks.find_store(str(self.root / "01-notes" / "01a-atomic" / "joining-network.md"))
        self.assertEqual(Path(found).resolve(), self.root.resolve())

    def test_find_returns_none_outside_a_store(self) -> None:
        with tempfile.TemporaryDirectory() as other:
            self.assertIsNone(cks.find_store(other))


class SinceTests(StoreFixture):
    """CI mode: old faults never block; only new ones fail."""

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.root), *args],
            check=True,
            capture_output=True,
            env={
                "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
                "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                "PATH": "/usr/bin:/bin:/usr/local/bin",
            },
        )

    def setUp(self) -> None:
        super().setUp()
        self.write("01-notes/01a-atomic/old-orphan.md", "# Old orphan\n")
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.git("tag", "base")

    def test_old_faults_do_not_fail(self) -> None:
        self.assertEqual(cks.since(str(self.root), "base"), [])

    def test_new_bad_name_fails(self) -> None:
        self.write("01-notes/01a-atomic/Bad_Name.md", "# Bad\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "bad name")
        self.assertIn("names", [c for c, _, _ in cks.since(str(self.root), "base")])

    def test_rise_in_orphans_fails(self) -> None:
        self.write("01-notes/01a-atomic/new-orphan.md", "# New orphan\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "orphan")
        self.assertIn("orphans", [c for c, _, _ in cks.since(str(self.root), "base")])


if __name__ == "__main__":
    unittest.main()

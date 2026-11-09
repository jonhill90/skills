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
        self.assertEqual(self.faults("99-meta/SPEC.md"), [])
        self.assertEqual(self.faults("05-archive/old-batch/SYNTHESIS.md"), [])

    def test_date_in_name_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/plan-2026-11-03.md"))

    def test_id_token_in_name_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/bl-0166-skill.md"))

    def test_version_suffix_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/plan-v2.md"))

    def test_catch_all_word_fails(self) -> None:
        self.assertTrue(self.faults("01-notes/01a-atomic/misc.md"))

    def test_batch_number_allowed_only_on_batch_hubs(self) -> None:
        # ORGANIZE 1.14 and 1.15: a batch is one hub note in 01rb-batches, never a numbered folder.
        self.assertEqual(self.faults("01-notes/01r-research/01rb-batches/0107-graphs.md"), [])
        self.assertTrue(self.faults("01-notes/01r-research/0107-graphs", True))
        self.assertTrue(self.faults("01-notes/01a-atomic/0107-graphs", True))
        self.assertTrue(self.faults("01-notes/01r-research/01rb-batches/graphs.md"))

    def test_research_holds_only_its_kind_folders(self) -> None:
        for kind in ("01ra-atomic", "01rc-check", "01rd-deviations", "01re-evidence",
                     "01rl-ledger", "01rp-protocol", "01rs-synthesis"):
            self.assertEqual(self.faults(f"01-notes/01r-research/{kind}/2026110719250001.md"), [])
            self.assertTrue(self.faults(f"01-notes/01r-research/{kind}/some-words.md"))
        self.assertTrue(self.faults("01-notes/01r-research/graphs", True))
        self.assertTrue(self.faults("01-notes/01r-research/01rx-misc/2026110719250001.md"))

    def test_note_named_by_its_id(self) -> None:
        # ORGANIZE 1.11: YYYYMMDDhhmmss## in Eastern time, counter 01-99.
        self.assertEqual(self.faults("01-notes/01a-atomic/2026110719250001.md"), [])
        self.assertTrue(self.faults("01-notes/01a-atomic/2026110719250000.md"))
        self.assertTrue(self.faults("01-notes/01a-atomic/2026133119250001.md"))
        self.assertTrue(self.faults("03-areas/2026110719250001.md"))
        self.assertEqual(self.faults("01-notes/01m-meetings/meeting-2026110719250001.md"), [])
        self.assertTrue(self.faults("01-notes/01a-atomic/meeting-2026110719250001.md"))

    def test_day_log_is_named_by_its_date(self) -> None:
        self.assertEqual(self.faults("01-notes/01d-daily/20261108.md"), [])
        self.assertTrue(self.faults("01-notes/01a-atomic/20261108.md"))

    def test_task_is_named_by_its_id(self) -> None:
        # ORGANIZE 1.22: one note per task in 01-notes/01t-tasks.
        self.assertEqual(self.faults("01-notes/01t-tasks/2026110723150001.md"), [])
        self.assertEqual(self.faults("01-notes/01t-tasks/01t-tasks.md"), [])
        self.assertTrue(self.faults("01-notes/01t-tasks/save-the-secret.md"))

    def test_repo_note_is_named_by_its_repository(self) -> None:
        # ORGANIZE 1.24: a script names a repo note <owner>-<repo>.md, digits and version words included.
        self.assertEqual(self.faults("04-resources/04r-repos/owner-tool-v2.md"), [])
        self.assertEqual(self.faults("04-resources/04r-repos/fedia-2211-notes.md"), [])
        self.assertTrue(self.faults("04-resources/04r-repos/Owner_Tool.md"))
        self.assertTrue(self.faults("04-resources/04c-clippings/page-v2.md"))

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
        self.assertEqual(self.faults("05-archive/old-export/sources/Paper_2024.pdf"), [])
        self.assertEqual(self.faults("01-notes/01h-handbook/01hd-data/Raw_Export.JSON"), [])


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

    def test_data_file_linked_from_its_note_is_reached(self) -> None:
        # ORGANIZE 1.15 and 1.17: no item folders in 01-notes; a file that is not a note sits in a
        # lettered sub-kind of its kind folder and is reached by the note that links it.
        self.write("01-notes/01a-atomic/01ad-data/hosts.csv", "a,b\n")
        self.write(
            "01-notes/01a-atomic/joining-network.md",
            CLEAN_STORE["01-notes/01a-atomic/joining-network.md"] + "\n[hosts](01ad-data/hosts.csv)\n",
        )
        self.write(
            "01-notes/01a-atomic/README.md",
            CLEAN_STORE["01-notes/01a-atomic/README.md"] + "- [01ad-data](01ad-data/hosts.csv): data files the notes cite\n",
        )
        self.assertEqual(self.faults(), [])

    def test_item_folder_in_notes_fails(self) -> None:
        self.write("01-notes/01a-atomic/joining-network/data/hosts.csv", "a,b\n")
        self.assertIn("folders", self.checks())


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

    def test_project_is_one_map_note_never_a_folder(self) -> None:
        # ORGANIZE 1.6 and 1.8: a project's plans are notes of their kind, linked from its map note.
        self.write("02-projects/README.md", "# Projects\n\n- [move](move.md): moving the store\n")
        self.write("02-projects/move.md", "# Move\n\n- [plan](move/plan.md): the steps in order\n")
        self.write("02-projects/move/plan.md", "# Plan\n")
        rows = [p for c, p, _ in self.faults() if c == "maps"]
        self.assertIn("02-projects/move/", rows)

    def test_day_log_is_mapped_by_its_hub(self) -> None:
        self.write("01-notes/README.md", CLEAN_STORE["01-notes/README.md"] + "- [01d-daily](01d-daily/01d-daily.md): one log per day\n")
        self.write("01-notes/01d-daily/01d-daily.md", "# Daily\n\n- [20261108](20261108.md): the work of one day\n")
        self.write("01-notes/01d-daily/20261108.md", "# 2026-11-08\n")
        self.assertEqual(self.faults(), [])


    def test_repo_note_is_covered_by_the_notes_that_cite_it(self) -> None:
        # ORGANIZE 1.24: 04r-repos holds one link note per repository, made by a script; no map lists it.
        self.write("README.md", CLEAN_STORE["README.md"] + "- [04-resources](04-resources/04-resources.md): made by others\n")
        self.write("04-resources/04-resources.md", "# Resources\n\n- [04r-repos](04r-repos/04r-repos.md): one note per repository\n")
        self.write("04-resources/04r-repos/04r-repos.md", "# Repos\n\n- [owner/tool](owner-tool.md): a tool our notes cite\n")
        self.write("04-resources/04r-repos/owner-tool.md", "---\nurl: https://github.com/owner/tool\n---\n# owner/tool\n")
        self.assertEqual([f for f in self.faults() if f[0] == "maps"], [])


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


class FolderNoteHubTests(StoreFixture):
    def test_folder_note_named_for_its_folder_is_the_hub(self) -> None:
        # ORGANIZE 1.5: below the root a folder's note is <folder>/<folder>.md; README.md still counts.
        (self.root / "01-notes/01a-atomic/README.md").unlink()
        self.write("01-notes/01a-atomic/01a-atomic.md", CLEAN_STORE["01-notes/01a-atomic/README.md"])
        self.write("01-notes/README.md", "# Notes\n\n- [01a-atomic](01a-atomic/01a-atomic.md): one idea per note\n")
        self.assertEqual(self.faults(), [])


RESEARCH_HUB = "01-notes/01r-research/01rb-batches/0001-demo.md"
RESEARCH_NOTE = "01-notes/01r-research/01re-evidence/2026110719250001.md"


class ResearchTests(unittest.TestCase):
    def test_note_names_its_batch_and_the_hub_links_it(self) -> None:
        files = {RESEARCH_NOTE, RESEARCH_HUB}
        ok = {RESEARCH_NOTE: "---\nbatch: 0001-demo\n---\n# x\n"}
        self.assertEqual(cks.research_faults(files, ok, {RESEARCH_HUB: [RESEARCH_NOTE]}), [])
        self.assertEqual(len(cks.research_faults(files, ok, {})), 1)
        self.assertEqual(len(cks.research_faults(files, {RESEARCH_NOTE: "# x\n"}, {RESEARCH_HUB: [RESEARCH_NOTE]})), 1)
        bad = {RESEARCH_NOTE: "---\nbatch: 0009-none\n---\n"}
        self.assertEqual(len(cks.research_faults(files, bad, {RESEARCH_HUB: [RESEARCH_NOTE]})), 1)


TASK = "01-notes/01t-tasks/2026110723150001.md"
TASK_TEXT = "---\ntype: task\nlabel: TASK-0001\nexternal-refs: []\nstate: ready\n---\n# Save the secret\n"


class TaskTests(unittest.TestCase):
    def test_task_front_matter(self) -> None:
        # ORGANIZE 1.22: type, label and state are fixed; the backlog is a state, not a folder.
        self.assertEqual(cks.task_faults({TASK}, {TASK: TASK_TEXT}), [])
        for broken in (TASK_TEXT.replace("type: task", "type: note"),
                       TASK_TEXT.replace("TASK-0001", "backlog one"),
                       TASK_TEXT.replace("TASK-0001", "BL-0001"),
                       TASK_TEXT.replace("external-refs: []\n", ""),
                       TASK_TEXT.replace("external-refs: []", "external-refs: [owner/repo#12]"),
                       TASK_TEXT.replace("state: ready", "state: backlog")):
            self.assertEqual(len(cks.task_faults({TASK}, {TASK: broken})), 1)

    def test_external_refs_name_their_tracker(self) -> None:
        # ORGANIZE 1.26: the same task's keys in other trackers, as <system>:<key> strings.
        text = TASK_TEXT.replace("external-refs: []",
                                 'external-refs: ["github:owner/repo#12", linear:TEAM-3]')
        self.assertEqual(cks.task_faults({TASK}, {TASK: text}), [])

    def test_task_hub_is_not_a_task(self) -> None:
        hub = "01-notes/01t-tasks/01t-tasks.md"
        self.assertEqual(cks.task_faults({hub}, {hub: "# Tasks\n"}), [])


HANDBOOK = "01-notes/01h-handbook/2026110723150002.md"


class HandbookTests(unittest.TestCase):
    def test_handbook_note_names_its_kind(self) -> None:
        # ORGANIZE 1.27: the handbook is reference only; the kind is a field, not a guess from the title.
        ok = "---\nhandbook-kind: vocabulary\n---\n# Words\n"
        self.assertEqual(cks.handbook_faults({HANDBOOK}, {HANDBOOK: ok}), [])
        for broken in ("---\ntitle: Plan\n---\n# Plan\n", "---\nhandbook-kind: plan\n---\n# Plan\n"):
            self.assertEqual(len(cks.handbook_faults({HANDBOOK}, {HANDBOOK: broken})), 1)

    def test_hub_and_runbooks_are_not_checked(self) -> None:
        hub = "01-notes/01h-handbook/01h-handbook.md"
        runbook = "01-notes/01h-handbook/01hr-runbooks/2026110723150003.md"
        texts = {hub: "# Handbook\n", runbook: "---\ntitle: Steps\n---\n"}
        self.assertEqual(cks.handbook_faults(set(texts), texts), [])


class TagTests(unittest.TestCase):
    def test_body_tag_fails_and_code_or_numbers_do_not(self) -> None:
        self.assertEqual([t for _, t in cks.body_tags("# Title\n\nsee #kubernetes here\n")], ["kubernetes"])
        self.assertEqual(cks.body_tags("# Title\n\nissue #490 and `#code` and C#\n\n```\n#fenced\n```\n"), [])
        self.assertEqual(cks.body_tags("---\ntags: [a]\n---\n# Heading\n"), [])

    def test_body_tag_line_number_counts_front_matter(self) -> None:
        self.assertEqual(cks.body_tags("---\ntitle: x\n---\n\n#tag\n"), [(5, "tag")])

    def test_kind_and_month_tags(self) -> None:
        # ORGANIZE 1.23: the kind words of the folder and the month MM-YYYY from created or the id.
        note = "01-notes/01a-atomic/2026110719250001.md"
        good = {note: "---\nid: 2026110719250001\ntags: [note, 11-2026, networking]\n---\n# x\n"}
        self.assertEqual(cks.tag_faults(good), [])
        self.assertEqual(len(cks.tag_faults({note: good[note].replace("note, ", "")})), 1)
        self.assertEqual(len(cks.tag_faults({note: good[note].replace("11-2026, ", "")})), 1)
        self.assertEqual(cks.tag_faults({note: "---\nid: 2026110719250001\n---\n# no tags line\n"}), [])
        self.assertEqual(cks.tag_faults({"05-archive/x.md": "---\ntags: []\n---\n"}), [])


AREA_TEMPLATE = """# Area map template

Catch-all section: Purpose

```markdown
# <Area>

## Purpose

<why>

<!-- map: start (written by org_check.py --maps-write) -->

- [<Name>](<path>): <reason>

<!-- map: end -->
```
"""


class ShapeTests(StoreFixture):
    def test_maps_write_puts_a_map_in_shape_and_the_check_passes(self) -> None:
        # ORGANIZE 1.7: one template per map kind; the link block is written, not hand-sorted.
        self.write("99-meta/templates/area-map.md", AREA_TEMPLATE)
        self.write("99-meta/templates/templates.md", "# Templates\n\n- [area-map](area-map.md): the area map shape\n")
        self.write("99-meta/README.md", CLEAN_STORE["99-meta/README.md"] + "- [templates](templates/area-map.md): map templates\n")
        self.assertIn("shape", self.checks())
        code, _ = self.run_main(str(self.root), "--maps-write")
        self.assertEqual(code, 0)
        text = (self.root / "03-areas/networking.md").read_text()
        self.assertIn("## Purpose", text)
        self.assertIn("## Atomic notes", text)
        self.assertNotIn("shape", self.checks())

    def test_store_without_templates_has_no_shape_check(self) -> None:
        self.assertNotIn("shape", self.checks())


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


    def test_bad_ref_exits_two(self) -> None:
        code, out = self.run_main(str(self.root), "--since", "no-such-ref")
        self.assertEqual(code, 2)
        self.assertIn("not a commit", out)

    def test_store_absent_at_ref_counts_as_empty(self) -> None:
        sub = self.root / "docs" / "knowledge"
        sub.mkdir(parents=True)
        for rel, text in CLEAN_STORE.items():
            path = sub / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "adopt the standard")
        self.assertEqual(cks.since(str(sub), "base"), [])

    def test_name_restored_from_another_branch_is_not_new(self) -> None:
        self.git("checkout", "-q", "-b", "side")
        self.write("01-notes/01a-atomic/Old_Name.md", "# Old\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "side")
        self.git("checkout", "-q", "main")
        self.git("checkout", "-q", "-b", "work")
        self.git("checkout", "side", "--", "01-notes/01a-atomic/Old_Name.md")
        self.git("commit", "-q", "-m", "bring it back")
        self.assertNotIn("names", [c for c, _, _ in cks.since(str(self.root), "base")])


class AdoptionTests(unittest.TestCase):
    def test_minimal_store_from_the_adoption_steps_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "README.md": (
                    "# Store\n\nBefore saving, run the wizard in 99-meta/ORGANIZE.md; to find "
                    "anything, follow the hub lists from here.\n\n"
                    "- [99-meta](99-meta/README.md): how this store works\n"
                ),
                "99-meta/README.md": "# Meta\n\n- [ORGANIZE](ORGANIZE.md): the wizard and naming rule\n",
                "99-meta/ORGANIZE.md": "# Organization standard\n",
            }
            for rel, text in files.items():
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(text)
            self.assertEqual(cks.check(str(root)), [])


if __name__ == "__main__":
    unittest.main()

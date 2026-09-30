"""Tests for scripts/skills_table.py; these do not execute any skill."""
import importlib.util
import pathlib
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('skills_table', pathlib.Path(__file__).parents[1]/'scripts/skills_table.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class SkillsTable(unittest.TestCase):
    def skill(self, root, name, body='Think carefully.', extra=''):
        p=root/'skills'/name; p.mkdir(parents=True)
        (p/'SKILL.md').write_text(f'---\nname: {name}\ndescription: Fixture purpose.\n---\n{body}\n{extra}')
        return p

    def readme(self, root):
        (root/'README.md').write_text('# Test\n\n'+m.START+'\n'+m.END+'\n')

    def test_static_packaging_reports_dependencies_with_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);p=self.skill(root,'visible',body='Run `gh pr list` in a terminal.')
            self.assertEqual(m.packaging(p)['status'],'FAIL')
            (p/'SKILL.md').write_text('---\nname: visible\ndescription: D\n---\nCompare the two supplied documents.\n')
            self.assertEqual(m.packaging(p)['status'],'PASS')

    def test_historical_cli_example_is_not_a_runtime_requirement(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            p=self.skill(root,'visible',body='Compare supplied evidence.\n## Where this came from\nSomeone ran `gh auth status` in an old incident.')
            self.assertEqual(m.packaging(p)['status'],'PASS')

    def test_table_lists_every_skill_with_its_audit_and_no_eval_column(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            self.skill(root,'alpha');self.skill(root,'beta',body='Run `gh pr list` in a terminal.')
            text=m.render(m.rows(root))
            self.assertIn('| Skill | Upload audit |',text)
            self.assertIn('| [`alpha`](skills/alpha/) | PASS |',text)
            self.assertIn('| [`beta`](skills/beta/) | FAIL |',text)
            self.assertNotIn('Eval',text)

    def test_write_is_deterministic_and_stale_check_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);self.skill(root,'visible');self.readme(root)
            self.assertEqual(m.write_table(root,check=False),0)
            self.assertEqual(m.write_table(root,check=True),0)
            self.skill(root,'added')
            self.assertEqual(m.write_table(root,check=True),1)

    def test_writes_nothing_but_the_readme(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);self.skill(root,'visible');self.readme(root)
            m.write_table(root,check=False)
            self.assertEqual(sorted(p.name for p in root.iterdir()),['README.md','skills'])

if __name__=='__main__':unittest.main()

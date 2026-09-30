#!/usr/bin/env python3
"""Generate README.md's "Skills in this collection" table from skills/.

Default mode rewrites the table; --check exits 1 if it is stale. Upload audit
is a static check for local-machine or CLI assumptions that would stop a skill
working where no shell is available: PASS means none were detected, not that
the skill was run anywhere. Writes nothing except README.md.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re

START = '<!-- generated-skills:start -->'
END = '<!-- generated-skills:end -->'
REPO = Path(__file__).resolve().parents[1]


def discover(directory):
    return [p for p in sorted(directory.iterdir()) if (p/'SKILL.md').is_file()] if directory.is_dir() else []


def packaging(skill):
    """Static upload-shape audit, not a claim of tested cross-harness behavior."""
    findings=[]
    patterns=[('machine-path',r'/Users/[^\s`]+|/Applications/[^\s`]+|~/[A-Za-z.]'),
              ('cli-dependency',r'(?:`|^\s*)(?:gh|tmux|obsidian|linear|uv|python3|pip|brew|sqlite3|npx) (?:auth|search|list|install|add|run|test|new-session|send-keys|wait-for|version|pr|issue|capture-pane|status|validate|skills|scripts/|/)'),
              ('shell-instructions',r'^```(?:bash|sh|shell|zsh)\s*$'),
              ('external-vault',r'\$AGENT_MEMORY_VAULT'),
              ('external-skill-reference',r'\]\(\.\./[^)]+SKILL\.md\)')]
    # Audit instructions and bundled Markdown references.
    files=[skill/'SKILL.md']+sorted((skill/'references').glob('*.md'))
    for p in files:
        historical=False
        for n,line in enumerate(p.read_text().splitlines(),1):
            if line.startswith('## '):
                historical=line == '## Where this came from'
            if historical:
                continue
            for label,pattern in patterns:
                if re.search(pattern,line):
                    findings.append({'reason':label,'file':f'skills/{skill.name}/'+p.relative_to(skill).as_posix(),'line':n})
    grouped={}
    for finding in findings:
        key=(finding['file'],finding['reason'])
        if key not in grouped:
            grouped[key]={**finding,'occurrences':0}
        grouped[key]['occurrences']+=1
    return {'status':'FAIL' if findings else 'PASS','findings':list(grouped.values()),
            'meaning':'Static upload-only audit: flagged local/CLI assumptions need review; PASS means none detected, not a web execution test.'}


def rows(root):
    return [{'name':skill.name,'packaging':packaging(skill)} for skill in discover(root/'skills')]


def render(table_rows):
    lines=[START,'',f"Generated from {len(table_rows)} skills; do not hand-edit.",
        'Regenerate with `python3 scripts/skills_table.py`; verify with `--check`.',
        'Upload audit PASS = no local-machine or CLI assumptions detected; FAIL = review before using without a shell.',
        '','| Skill | Upload audit |','|---|---|']
    lines+=[f"| [`{row['name']}`](skills/{row['name']}/) | {row['packaging']['status']} |" for row in table_rows]
    lines+=['',END]
    return '\n'.join(lines)


def write_table(root, check=False):
    readme=root/'README.md';text=readme.read_text()
    if text.count(START)!=1 or text.count(END)!=1:
        raise ValueError('README must have exactly one generated-skills section')
    table_rows=rows(root)
    start=text.index(START);end=text.index(END)+len(END)
    updated=text[:start]+render(table_rows)+text[end:]
    if updated==text:
        print(('Verified' if check else 'Generated')+f" {len(table_rows)} skills; unchanged")
        return 0
    if check:
        print('STALE: README.md skills table; run python3 scripts/skills_table.py');return 1
    readme.write_text(updated)
    print(f"Generated {len(table_rows)} skills; README.md updated")
    return 0


def main():
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check',action='store_true',help='exit 1 if the README table is stale')
    return write_table(REPO,parser.parse_args().check)


if __name__=='__main__':
    raise SystemExit(main())

# Eval scenario: ops vault lookup

Given to both arms verbatim, identical except for the skill-loading
instruction noted at the bottom.

---

You have access to a local directory: `fixture/vault/`. It contains
`index.md` (one line per note) and `facts/` (100 individual note files,
`fact-001.md` through `fact-100.md`).

**Task:** Answer this exactly, and nothing else:

> What is the configured maximum retry backoff, in seconds, for the
> `ingest-worker` service?

Requirements:

- Give the number, and name the exact note file (`fact-NNN.md`) it came
  from.
- Do not guess. If you are not confident of the number from what you
  actually read, say so instead of stating one.
- As your last action, write `manifest.json` to the current directory:
  `{"answer_seconds": <int or null>, "source_file": "<fact-NNN.md or null>",
  "files_opened": ["index.md", "facts/fact-XXX.md", ...]}` — the exact,
  ordered list of every file under `fixture/vault/` you actually opened,
  including the index. This is not a summary of what you would recommend
  reading; it is a literal log of every read.

---

**Arm A only** (progressive-disclosure loaded): before starting, read
`skills/progressive-disclosure/SKILL.md` in this repository and follow
its discipline for this task.

**Arm B only**: no additional instruction. Solve it however seems
natural.

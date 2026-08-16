# Worked example: judging extracted rows

This is a synthetic case, not real transcript data — safe to read, copy, or
extend without touching anyone's actual history. It exercises the three
outcomes [`SKILL.md`](../SKILL.md)'s judgement step must tell apart: a term
that is repeated tooling, a term that is repeated boilerplate, and a term
that is a genuine re-made decision. A rewrite of this skill's judgement
guidance that can't reproduce these three verdicts from these rows has
regressed, regardless of how the extraction half changed.

## Input

Rows shaped like `mine_prompts.py --json` output, trimmed to the fields
that matter for judgement (`text`, `source`). Assume all three terms passed
the positive-control check (`--stats` returns nonzero) and cleared
`--typed-only`.

```json
[
  {"term": "gh pr create", "source": "session-a.jsonl",
   "text": "run gh pr create with the usual title format"},
  {"term": "gh pr create", "source": "session-c.jsonl",
   "text": "gh pr create --fill, then link the issue"},
  {"term": "gh pr create", "source": "session-f.jsonl",
   "text": "open the PR with gh pr create once tests are green"},

  {"term": "Delivering this work", "source": "session-b.jsonl",
   "text": "## Delivering this work\nUnless this brief says otherwise, when you are finished: push your branch and open a PR."},
  {"term": "Delivering this work", "source": "session-d.jsonl",
   "text": "## Delivering this work\nUnless this brief says otherwise, when you are finished: push your branch and open a PR."},
  {"term": "Delivering this work", "source": "session-e.jsonl",
   "text": "## Delivering this work\nUnless this brief says otherwise, when you are finished: push your branch and open a PR."},

  {"term": "verify before reporting absence", "source": "session-a.jsonl",
   "text": "before you tell me it found nothing, check the tool actually works on a case you know is true"},
  {"term": "verify before reporting absence", "source": "session-c.jsonl",
   "text": "a zero result from a script that's never been checked against a known case isn't evidence of anything"},
  {"term": "verify before reporting absence", "source": "session-g.jsonl",
   "text": "don't tell me it's absent until you've proven the search itself works"}
]
```

## Expected judgement

| Term | Verdict | Why |
|---|---|---|
| `gh pr create` | **Not a candidate — repeated tool call.** | Same CLI invocation, different surrounding wording each time, no re-derived reasoning attached. This is the tool-vs-decision question from step 2. |
| `Delivering this work` | **Not a candidate — template boilerplate.** | Byte-identical text across all three sources, same heading, same slot in what is evidently a shared template. High count and multi-source spread, but no re-derivation — this is the decision-vs-boilerplate question from step 3, and the one a tool's consistency score alone cannot make (identical text scores as maximally "consistent," which is exactly backwards here). |
| `verify before reporting absence` | **Candidate.** | Same underlying rule, worded differently every occurrence, appearing in live correction/reasoning rather than a fixed template — the shape of a decision being re-made, not copy-pasted. Report it with count (3), source spread (3 distinct sessions), the reason above, and one or two trimmed snippets. |

## Using this case

Read the three rows for one term, decide the verdict using
[`SKILL.md`](../SKILL.md)'s judgement steps, then compare to the table
above. If a judgement pass on this synthetic input doesn't land on these
three verdicts, the guidance — not this fixture — is what needs fixing
before it's trusted on a real transcript set.

---
name: mine-transcripts
description: Mine your own agent transcripts for vocabulary you keep reaching for, to find candidates for the next skill — not to write one. Invokes the external mine_prompts.py extractor, then applies judgement the tool can't — separating a re-made decision from a repeated tool call or repeated boilerplate. User-invoked only, for a deliberate periodic review; never fire this mid-task just because something feels repetitive.
---

# Mine Transcripts

A word or phrase a person keeps reaching for is a procedure they keep
re-explaining. This skill finds that repetition in your own transcripts and
turns it into a ranked list of **candidates with evidence** — not a skill.
Every other skill in a typical collection encodes a known practice; this one
finds what has not been named yet, so that noticing does not depend on
someone happening to notice.

## Reach for this when

- You are deliberately reviewing your own transcripts for skill
  opportunities — a periodic pass, done on purpose.

## Do not reach for this when

- Mid-task, because you or the user just said "we keep doing this." That
  observation is worth a note for the next review, not a mining run right
  now. A skill that fired on that sentence would interrupt constantly and
  would still only produce a candidate list, not the fix the user wants in
  the moment.
- You already know what the next skill should be. Mining finds candidates
  when the pattern isn't obvious yet; it adds nothing once it is.

## Extraction is a tool's job now, not the model's

Filtering JSONL by shape — which turns are harness noise, which are
site-specific recurring prompts, which look typed versus pasted, which fall
in a date range or match a grep — is deterministic. It has one correct
answer per input, and re-deriving that answer by reading transcripts by eye
every run is a model doing a fixed job forever
([jonhill90/skills#207](https://github.com/jonhill90/skills/issues/207)).

That job now lives in `mine_prompts.py`, part of the
[`agent-supervisor`](https://github.com/jonhill90/agent-supervisor) project
— **not bundled in this collection**, because it is harness machinery, not
skill content. Confirm it's on the machine before relying on it (`find
</path/to/agent-supervisor> -name mine_prompts.py` or ask where that repo is
checked out). If it isn't available, say so and stop — walking through its
extraction logic by hand is exactly the fixed-job-forever this rewrite
removes; don't reintroduce it because the tool is momentarily missing.

The tool takes:

- `--root` — transcript root (defaults to `~/.claude/projects`; override for
  another harness).
- `--since YYYY-MM-DD` — restrict to a date range.
- `--grep <pattern>` — restrict to turns matching a regex.
- `--typed-only` — heuristic: keep only turns that look typed (short, few
  newlines, no code fence) and drop turns that look pasted (skill files,
  briefs, API docs). It is a heuristic, not a guarantee — of one measured
  corpus, roughly 46% of extracted turns were pasted, not typed, so a plain
  `--grep` without `--typed-only` will hit pasted material too.
- `--stats` — counts per day, plus a typed/pasted split. Use this first, see
  [Verify the instrument](#verify-the-instrument-before-trusting-a-result).
- `--json` — machine-readable rows (`at`, `text`, `typed`, `source`), for
  reading programmatically instead of scrolling terminal output.

What it will never do: reason about what a turn *means*, decide whether a
repeated term is a re-made decision, or tell you a request recurred because
it was never delivered. That's this skill's job, below — it starts only
after the tool's output exists.

## What this reads, and what it must never emit

Settle this before running anything — it governs every step below.

- **Read-only.** Both the extractor and this skill only read transcript
  files; neither writes, moves, or deletes them. If the transcript root is
  under `$HOME` (it usually is), say so out loud before scanning: *"reading
  `~/...`, read-only."*
- **No network calls, ever.** Nothing about a transcript's content leaves
  the local machine. This includes not pasting raw extracted turns into an
  issue, message, or any other outward-facing tool without redacting first.
  `mine_prompts.py` does not redact — it prints operator turns verbatim, by
  design, on the assumption its output stays local. Treat every row it
  returns as unredacted until you've handled it.
- **What you may quote outward.** A short (roughly one sentence) trimmed
  snippet as evidence for a candidate, hand-checked for anything sensitive
  before it leaves this skill's working notes — never a full turn, a full
  file, or a full command line.
- **What must never leave this machine.** Credentials, tokens, or keys;
  anything that reads as employer-owned or project-specific material;
  third-party names beyond what the evidence strictly needs; private
  repository content.
- **When in doubt, drop the quote.** A candidate is still evidenced by its
  term, count, and file-spread alone. A preference can be *described*
  without being *quoted* — characterise it, don't paste it, whenever the
  description carries the same evidence.
- **The output stays local until you decide otherwise.** Write the ranked
  list to a scratch file. Do not open an issue, send a message, or commit
  the list anywhere without a separate, deliberate decision to do so — and
  redact again at that boundary, because the bar for something staying on
  your own disk is lower than the bar for something leaving it.

## Verify the instrument before trusting a result

Run `mine_prompts.py --stats` with no filters before anything else. It must
return a nonzero count for turns you already know exist. If it doesn't,
the tool's harness-noise filter or your `--root` is wrong — fix that before
believing any downstream zero or thin result.

This was a real failure, not a hypothetical: the extractor's predecessor
returned 80 "candidates" that were all JSON envelope noise (`tokens`,
`cache`, `sessionId`) because raw transcript bytes are JSON-per-line and
most byte volume is API metadata, not anything a human typed
([jonhill90/skills#199](https://github.com/jonhill90/skills/issues/199)).
The instrument was wrong, not the corpus. `mine_prompts.py` itself refuses
to print an empty, confident-looking result — an unfiltered, no-match run
exits nonzero with a message on stderr telling you to verify the instrument
first — but that only catches the *total-absence* case. A `--grep` or
`--since` filter that quietly returns nothing looks identical to "he never
said that" and to "the filter is wrong"; treat both as open until you've
checked the unfiltered stats.

**The corpus itself is also incomplete**, separately from any tool bug: one
measured phrase — said and quoted verbatim elsewhere (a personal vault) —
had **no matching original turn** across 1,150 transcript files (could not
measure — no primary source found to confirm this count). Transcripts
are one record of what was said, not the only one. Before reporting "never
said" or "no evidence of," check whatever other record exists (notes,
vault, prior write-ups) — an absence in `mine_prompts.py`'s output is
evidence about the corpus's coverage, not about what the operator did or
didn't say.

## Split deterministic from judgement

Counting, filtering, and typed/pasted classification are deterministic —
`mine_prompts.py`'s job, and its output is inspectable text or JSON, not a
claim you have to trust. Deciding "this term names a procedure" is
judgement, and it happens next, by reading that output, not by re-scanning
transcripts yourself.

### 1. Run the tool

```bash
python3 /path/to/agent-supervisor/scripts/supervisor/mine_prompts.py --stats
python3 /path/to/agent-supervisor/scripts/supervisor/mine_prompts.py --typed-only --json > /tmp/mined.json
python3 /path/to/agent-supervisor/scripts/supervisor/mine_prompts.py --since 2026-08-01 --grep '<term>'
```

Start broad (`--stats`, no filters) as the positive control above, then
narrow with `--typed-only`, `--since`, and `--grep` once you trust the
instrument. `--typed-only` cuts pasted briefs and skill files out of a
plain word search; keep both typed and pasted runs in view when a term
might genuinely appear in either.

### 2. Cluster and count by eye

Unlike the old bundled script, `mine_prompts.py` does not compute a
consistency score — it hands you rows, not a ranked table. Group the rows
that share a term or phrase yourself (grep, or read `--json` output) and
for each candidate note: how many times it appears, across how many
distinct sessions (`source`), and whether the surrounding text reads the
same way each time.

### 3. Judge the candidates

For each term worth a look:

1. **Read the actual rows**, not just the count. Do they show the same
   kind of explanation each occurrence, or unrelated sentences that happen
   to share a word?
2. **Ask the tool-vs-decision question.** `gh`, `pytest`, `git` recur
   because they're invoked, not because a decision gets re-made — not a
   candidate. A term can also name a decision-shaped *use* of a tool
   ("always confirm before force-push") that no denylist catches; judge the
   use, not just the noun.
3. **Ask the decision-vs-boilerplate question — this is what a tool
   cannot do.** A phrase repeated across many dispatch briefs or templates
   can look exactly like a re-made decision by count and file-spread alone.
   Tell them apart by reading what surrounds the phrase each time: template
   boilerplate is copied verbatim, same wording, same slot, from a fixed
   source (a brief template, a prompt skeleton); a re-made decision is
   re-derived — worded differently each time, appearing in reasoning or
   correction, not in a fixed template slot. This distinction was a real
   finding in a prior run and the reason judgement stays a model's job
   here.
4. **Check whether a request recurred because it was never delivered**,
   not because it's a recurring practice. A term repeated across sessions
   can mean "the same fix keeps getting asked for" rather than "the same
   procedure keeps getting used" — read whether the surrounding turns show
   the request being satisfied, or being asked again.
5. **Check whether a decision was settled and later reopened**, and
   whether a correction repeats. Both are visible only in the surrounding
   text, not in the count.
6. **Check it isn't already a skill.** If an existing skill already covers
   the term, that's evidence the skill's `description` is doing its job,
   not a new candidate.
7. **Drop what you can't evidence.** A term with a few occurrences and no
   readable pattern in the rows is a lead, not a candidate — leave it out
   rather than padding the list.

### 4. Report the ranked list

One entry per surviving candidate:

- the term or phrase
- count and distinct-source spread
- one sentence on *why* it looks like a re-made decision rather than a
  repeated tool call or repeated boilerplate
- one or two hand-checked, trimmed snippets as evidence (see
  [What this reads, and what it must never emit](#what-this-reads-and-what-it-must-never-emit))

This list is the deliverable. It names candidates for the next skill; it is
not one. Turning a candidate into a skill is a separate, deliberate step —
in this collection, that means opening an issue the way
[jonhill90/skills#136](https://github.com/jonhill90/skills/issues/136)
records `distill` having been proposed, not filing one automatically from
this run.

## Worked example

[`references/eval-case.md`](references/eval-case.md) walks a small,
synthetic set of extracted rows through the judgement steps above —
including a term that's boilerplate, one that's a repeated tool call, and
one that's a genuine re-made decision — with the expected classification
for each. Use it to sanity-check that this skill's judgement guidance
actually discriminates before trusting it on a real transcript set.

## Notes

- This skill is public opt-in, not part of any default roster — rostering a
  skill and adding it here are separate decisions.
- `mine_prompts.py` lives outside this collection because it's harness
  machinery (transcript root, site-specific exclude list) not skill
  content. If a project needs an extractor bundled instead of external,
  that's a different skill for a different repository, not a reason to
  re-embed extraction logic here.

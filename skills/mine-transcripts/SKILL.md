---
name: mine-transcripts
description: Mine your own agent transcripts for vocabulary you keep reaching for, to find candidates for the next skill — not to write one. Ranks terms by frequency and by whether they're explained the same way every time, separating a re-made decision from a repeated tool invocation. User-invoked only, for a deliberate periodic review; never fire this mid-task just because something feels repetitive.
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

## What this reads, and what it must never emit

Settle this before running anything — it governs every step below.

- **Read-only.** This skill only opens files under the transcript directory
  you point it at, and never writes, moves, or deletes them. If that
  directory is under `$HOME` (it usually is — transcripts live wherever your
  harness stores session history), say so out loud before scanning: *"reading
  `~/...`, read-only."*
- **No network calls, ever.** Nothing about a transcript's content leaves the
  local machine. This includes not pasting raw snippets into an issue,
  message, or any other outward-facing tool without redacting first.
- **What it may quote.** A short (roughly one sentence) trimmed snippet as
  evidence for a candidate term, already redacted by
  [`scripts/mine-vocabulary.py`](scripts/mine-vocabulary.py) — never a full
  message, a full file, or a full command line.
- **What it must never emit.** Credentials, tokens, or keys (the script
  redacts common shapes automatically, but treat that as a floor, not a
  guarantee — re-check by eye); anything that reads as employer-owned or
  project-specific material; third-party names beyond what the evidence
  strictly needs; private repository content.
- **When in doubt, drop the quote.** A candidate is still evidenced by its
  term, count, and file-spread alone. If a snippet looks sensitive after
  redaction, keep the numbers and cut the quote rather than editing the
  quote by hand — hand-editing a snippet you're unsure about is how a
  partial redaction ships.
- **The output stays local until you decide otherwise.** Write the ranked
  list to a scratch file. Do not open an issue, send a message, or commit
  the list anywhere without a separate, deliberate decision to do so — and
  redact again at that boundary, because the bar for something staying on
  your own disk is lower than the bar for something leaving it.

## What counts as a candidate

Raw frequency is the wrong metric — "the", "file", "run" will dominate any
transcript. A candidate is a term that is **both** frequent **and** followed
by the same kind of explanation each time. That second condition is what
separates two reasons a term repeats:

- **A tool is used often.** `gh`, `pytest`, `git` recur because they're
  invoked, not because a decision gets re-made. Not a candidate.
- **A decision is re-made every time.** The term shows up attached to the
  same reasoning, the same trade-off, the same check, regardless of which
  transcript it's in. That repetition is the signal — an unnamed practice
  that has earned a name.

[`scripts/mine-vocabulary.py`](scripts/mine-vocabulary.py) approximates the
second condition with a **consistency score**: for each occurrence of a
term, it takes the surrounding words as a small context set, then measures
how much those context sets overlap across occurrences. A term whose context
keeps overlapping is explained the same way each time; a term whose context
is different every time is just common. The script also flags common CLI
tool names as `likely_tool` and excludes them from the ranked output by
default — a deterministic prior on the first false-positive class, not a
verdict on the second.

## Split deterministic from judgement

Counting, clustering, and redaction are deterministic — they live in the
script and their output is inspectable JSON, not a claim you have to trust.
Deciding "this term names a procedure" is judgement, and it happens next,
by reading that JSON, not by re-scanning the transcripts yourself.

### 1. Run the script

```bash
python3 scripts/mine-vocabulary.py <transcript-dir> --min-count 3 --min-files 2
```

- `<transcript-dir>` — wherever your harness stores session transcripts.
  There is no default; point it explicitly, and say read-only when you do.
- `--min-count` / `--min-files` — raise these on a large transcript set to
  cut noise before you start reading; the defaults (3 occurrences, 2 files)
  are a floor, not a target.
- `--include-tools` — keep `likely_tool`-flagged terms in the output, for
  when you want to sanity-check the denylist itself rather than trust it.
- `--self-test` — run the bundled fixture check with no transcripts
  involved; use it to confirm the script works in this environment before
  pointing it at real data.

Each result carries `term`, `count`, `distinct_files`, `consistency`,
`likely_tool`, and up to three redacted `sample_snippets`.

### 2. Judge the candidates

Read the JSON, highest `count × (1 + consistency)` first (that is already
the script's sort order). For each term worth a look:

1. **Read the sample snippets.** Do they show the same kind of explanation,
   or unrelated sentences that happen to share a word? High `consistency`
   is a hint, not a verdict — read the evidence before trusting the number.
2. **Ask the tool-vs-decision question directly**, even for terms the script
   didn't flag `likely_tool`. A term can name a decision-shaped *use* of a
   tool ("always confirm before force-push") that the script's denylist
   can't see, or can be a project-specific noun that isn't a CLI tool but
   still isn't a procedure (a file name, a person's name).
3. **Check it isn't already a skill.** If an existing skill already covers
   the term, it's evidence that skill's `description` is doing its job, not
   a new candidate.
4. **Drop what you can't evidence.** A term with three occurrences and no
   readable pattern in the snippets is a lead, not a candidate — leave it
   out rather than padding the list.

### 3. Report the ranked list

One entry per surviving candidate:

- the term
- count and distinct-file spread
- one sentence on *why* it looks like a re-made decision rather than a
  repeated tool call
- one or two redacted sample snippets as evidence

This list is the deliverable. It names candidates for the next skill; it is
not one. Turning a candidate into a skill is a separate, deliberate step —
in this collection, that means opening an issue the way
[jonhill90/skills#136](https://github.com/jonhill90/skills/issues/136)
records `distill` having been proposed, not filing one automatically from
this run.

## Bundled scripts

| Script | Use |
|---|---|
| `mine-vocabulary.py` | deterministic counting, clustering, and redaction pass over a transcript directory; read-only |

`.jsonl` files get one extra step first: session transcripts like Claude
Code's are JSON-per-line, and most of that JSON is API envelope (token
counts, cache metadata, UUIDs) rather than anything anyone said. The script
parses each line, keeps only `user`/`assistant` turns, and extracts their
`text`/`thinking` content before counting — pointed straight at raw
transcript bytes, envelope fields alone filled every ranked slot
(jonhill90/skills#199). A `.jsonl` file that doesn't parse as transcript
JSON is scanned as plain text, unchanged from before.

## Notes

- This skill is public opt-in, not part of any default roster — rostering a
  skill and adding it here are separate decisions, and this one has not
  been measured against real transcripts yet.
- The script's stopword and tool-token lists are deliberately small and
  generic. They will under-filter on a first run; tune `--min-count` and
  read the snippets rather than growing the lists to fit one transcript
  set.

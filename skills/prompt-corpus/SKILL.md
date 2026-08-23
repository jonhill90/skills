---
name: prompt-corpus
description: Turn a transcript history into a queryable record of decisions — raw prompts, one judgement per prompt, and views that answer "what is still binding", "what did I say that nobody acted on", and "what did I ask that was never answered". Use when adding new prompts to the corpus, when re-running the judging pass, or when answering a question about what the operator has already decided.
---

# Prompt corpus

A chat archive answers *what did I say*. This answers *what is still binding,
what did nobody act on, and what did I ask that was never answered* — which is
a different thing and needs a different shape.

The whole design rests on one boundary: **a model runs ONCE per prompt, at
write time. Every read afterwards is plain SQL.** Break that and this becomes
another thing that needs inference to answer a question, which is what it
exists to replace.

## The layers

```
prompts   raw + cleaned + context + project.  text_raw is IMMUTABLE.
items     one judgement per row: kind, body, weight, status, resolved_to
links     conflicts_with / supersedes / depends_on — recorded by hand, NEVER inferred
views     unacknowledged · live_parameters · open_questions · conflicts · possibility_count
```

`context` is `NOT NULL` and it is load-bearing, not decoration. "Live." means
nothing without knowing it answered "live terminal or refreshed preview?".

## The pipeline

```bash
itemize_prompts.py --extract [--limit N]   # pure SQL, decides nothing
<a model judges the extracted file>        # the ONE model step
itemize_prompts.py --load judged.json      # pure SQL, idempotent by hashed id
```

Item ids derive from `(prompt_id, index, body)`, so re-loading the same
judgements writes 0. Always verify that after a load — an idempotency claim
nobody tested is not a property.

At scale, run the judging as a dynamic workflow: `.claude/workflows/corpus-itemise.js`
on the `feat/prompt-corpus-skill` branch of `agent-supervisor` (could not measure
whether this has since merged to `main`). Agents judge and write JSON **only**; a single serial
agent does every ledger write. Twelve concurrent writers on one SQLite file
contend.

## The judging rules — these are the technique

Get these wrong and the corpus is worse than nothing, because it will look
authoritative while being wrong.

- **Every prompt gets an entry.** A prompt worth nothing durable gets ONE item
  with `kind=thought`, `weight=retracted`, `status=dropped` and a
  `status_reason`. Never omit one: `--extract` selects prompts with no `items`
  row, so an omitted prompt resurfaces at the head of every future batch,
  forever. This is the single most common mistake and two independent agents
  made it before it was written down.
- **`resolved_to` is only for things that CONSTRAIN** — `tooling=cli_first`,
  `ui_fidelity=1:1`. A question or a one-off directive has no `resolved_to`.
- **`weight=hard` means binding; `preference` means he leans that way.**
  Getting this wrong manufactures false conflicts. A preference was once
  treated as binding and cost a whole session.
- **Do not soften tone.** If he was blunt, the body stays blunt. You are
  recording what he meant, not making it polite.
- **Do not invent context.** If a prompt is ambiguous, say so in the body
  rather than guessing a meaning.
- **Noise is DROPPED WITH A REASON, never deleted.** An exclusion must be
  reviewable and reversible.

## Noise: structural markers only, never topic keywords

Matched literally, no model:

```
"do exactly what it says"        "That file is your complete brief"
"carry it out exactly as written"
"Base directory for this skill:" "## Context Usage"
"Supervisor loop tick"           "<local-command-stdout>"
```

**A topic-keyword filter is a trap.** Filtering on `career`/`resume` matched
`Hill90 resume sweep` and several real PR discussions. Structure is a property
of who wrote the text; topic is not.

## Traps, each of which cost real time

- **Do not sample with `order by length(text_raw) desc`.** It selects FOR
  machine text and produced a confident wrong conclusion that the corpus was
  mostly junk when 50 rows were.
- **Project provenance is not in `source_file`** — that is only a session
  UUID. Recover it from the transcript's directory under `~/.claude/projects/`,
  or capture it at write time from the hook's `cwd`.
- **The loader is not atomic.** It writes item-by-item with no transaction, so
  one malformed item leaves a partial write. Check what actually landed before
  re-running; ids are deterministic so a corrected re-run fills only the gap.
- **`kind` and `weight` are different axes.** `preference` is a WEIGHT. A judge
  emitting `kind: preference` is a schema error, not a judgement.
- **A missing `body` crashes the loader** with `KeyError`. Validate the judged
  file before loading it.

## Reading it

```sql
select count from possibility_count;   -- how many hard constraints are live
select * from unacknowledged;          -- said, never acted on
select * from open_questions;          -- asked, never answered
select * from live_parameters where weight='hard';
```

`conflicts` reports links someone recorded. It never infers one — deciding two
items genuinely contradict, rather than describing different scopes or one
superseding the other, is judgement and stays with something accountable.

## Before you answer a question about what the operator decided

**Query the corpus first.** That is what it is for, and forgetting to is the
most likely way this skill goes unused: the answer to "should we build X first"
is usually already in `live_parameters`, in his own words, with more authority
than a fresh opinion.

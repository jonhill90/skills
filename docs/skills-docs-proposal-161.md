# Should this repository have docs, and what should they say? (#161)

Proposal only — no docs are written here, and no files move. Jon reacts to
this; a follow-up PR implements whatever he picks. Same discipline
agent-dotfiles#143 used for the layout question, and it worked.

## The concrete reference: `mattpocock/skills`

Jon's own framing: *"i know i was thinking about how matt pocock has docs
in his skills repo and its docs."* Cloned and read directly
(`github.com/mattpocock/skills`, default branch `main`) rather than
summarised from reputation. Its structure, with paths:

```
README.md                          # pitch, install, "why these skills exist"
                                    # essay, and a reference table per bucket
AGENTS.md / CLAUDE.md               # identical — repo contribution rules
CONTEXT.md                          # this repo's OWN domain glossary,
                                    # produced by dogfooding its own
                                    # domain-modeling skill on itself
.agents/
  invocation.md                     # user- vs model-invoked, as a concept
  install-block.md                  # ONE canonical install wording, quoted
                                     # verbatim everywhere else needs it
  writing-docs.md                   # the doc-page template + authoring
                                     # rules for docs/ (page structure,
                                     # tone, linking rules, a "Done when"
                                     # checklist)
  adr/0001-*.md, 0002-*.md          # numbered architecture decisions
docs/
  engineering/<skill-name>.md       # one page per PROMOTED skill only
  productivity/<skill-name>.md      # (mirrors skills/engineering,
                                     #  skills/productivity 1:1)
skills/
  engineering/<name>/SKILL.md       # bucketed, not flat
  engineering/README.md             # bucket-local skill index
  productivity/<name>/SKILL.md
  productivity/README.md
  misc/, in-progress/, deprecated/  # NOT promoted, NOT in docs/, NOT in
                                     # the plugin manifest
.claude-plugin/plugin.json          # Agent-Plugins-adjacent manifest,
  .claude-plugin/marketplace.json   # explicit promoted-skills array
```

Concrete facts, not impressions:

- **35 total `SKILL.md` files, 25 promoted** (`engineering/` +
  `productivity/`) and listed in `plugin.json`'s `skills` array; the
  other 10 sit in `misc/`, `in-progress/`, `deprecated/` and are
  deliberately absent from the README, the plugin manifest, and `docs/`.
- **`docs/` pages exist only for the 25 promoted skills**, one file each,
  averaging ~90 lines (`docs/engineering/tdd.md` is 128 lines). They are
  published externally at `https://aihero.dev/skills-<name>` — the repo
  path is organisation only, not the served URL.
- **A page is not a copy of `SKILL.md`.** `.agents/writing-docs.md`
  states this explicitly and gives the page a fixed section frame —
  *What it does* (leads with the one-sentence job, then the *defining
  constraint* — the fact that makes it behave differently from the
  obvious default), *When to reach for it* (invocation mode + trigger
  boundary), optional *Prerequisites*, a free-form middle in the skill's
  own vocabulary, *Common questions* (sized to evidence actually found —
  the wiki, `gh issue list --search`, `CHANGELOG.md` — never padded),
  *It's working if*, always-present *Where it fits* (role + neighbours +
  a link to the router skill `ask-matt`). The rule that stands out most:
  **"A page carries no install commands"** — the hosting site renders
  the install widget itself, so a hand-written copy in the page would
  drift from it. That single rule is why `.agents/install-block.md`
  exists at all: one canonical block, quoted everywhere, changed once.
- **`README.md` does not restate what `docs/` says.** It carries the
  pitch, the two-philosophy install split (managed plugin vs. editable
  copy), a "why these skills exist" essay anchored to four named failure
  modes, and a flat reference table per bucket linking straight to each
  `SKILL.md` — not to the doc page. The doc pages are a separate,
  externally-hosted layer for someone who found one skill and wants to
  understand it, not someone browsing the whole set.
- **The authoring/contribution rules are `AGENTS.md`+`.agents/*.md`**,
  entirely separate from both `README.md` and `docs/`. `.agents/` covers
  bucket policy, the promoted-skill invariant, invocation classification,
  and the doc-page template itself — none of it consumer-facing.

## What a cold reader of `jonhill90/skills` cannot answer today

Read cold, this repo is 24 skills (flat, no buckets), `AGENTS.md`,
`CLAUDE.md`, `README.md`, `scripts/`, `tests/`. Concretely, today:

1. **`README.md`'s own table is wrong, not just thin.** It is headed
   "Skills in this collection" and lists exactly 13 rows — the 13 skills
   that existed on 2026-08-09 when `docs/` was removed (`069e2c4`). Eleven
   more skills merged 2026-08-11 (`ask-a-council`, `distill`,
   `keep-me-honest`, `loop-contract`, `loop-memory`, `mine-transcripts`,
   `notify`, `prd`, `spec`, `tdd`, `verify-the-instrument`) and the table
   was never touched. A cold reader sees a table that claims completeness
   and is silently 46% short — the identical shape as the roster gap
   agent-dotfiles#181 just fixed, one layer up, in the repo's own README
   instead of a consumer's install manifest.
2. **No skill has a page of its own anywhere.** `SKILL.md` is written for
   the *agent that runs the skill* — dense, imperative, front-loaded with
   trigger conditions. A human deciding whether `wayfinder`-equivalent
   `loop-contract` is the right tool for their situation, versus
   `loop-memory`, has only the one-line README description and the
   `SKILL.md` body itself to go on. There is no document written for a
   human's decision, only for the agent's execution.
3. **Nothing explains the user-invoked/model-invoked split as a concept.**
   `AGENTS.md` has one bullet: *"Classify each skill as model-invoked...
   or user-invoked... Express the classification in `description` trigger
   wording, not in frontmatter fields."* That is instruction for an
   *author*, not orientation for a *reader* — nowhere does this repo say,
   for a reader, "here is what that split means for you and how to tell
   which one you're looking at." (Contrast `mattpocock/skills`, where
   `.agents/invocation.md` is a dedicated concept page and both README
   levels group entries under **User-invoked**/**Model-invoked** headers.)
4. **No categorisation at all.** `mattpocock/skills` splits 24 promoted
   skills into two buckets your eye can scan; this repo's `skills/` is 24
   directories in one flat alphabetical list, and the README table is
   likewise flat. A reader cannot tell `create-skill` (repo-authoring
   tooling) from `notify` (an outbound-messaging utility) from
   `loop-contract` (a design discipline) except by reading each
   description in full.
5. **The install story is one command with no philosophy attached.**
   `npx skills add jonhill90/skills --skill <name>` is correct and
   sufficient mechanically, but it doesn't say anything about what
   installing means (a copy you own and can edit — this repo has no
   competing "managed bundle" mode, unlike `mattpocock/skills`'s
   plugin-vs-skills.sh split) or how updates are meant to be pulled back
   in later.
6. **No visible decision trail.** `provenance-manifest.md`,
   `SPEC.md` §10.1's evidence bar, and the eleven skills' own individual
   issues (`#129`, `#133`–`#137`, `#146`) are the actual record of *why*
   a skill exists and what it does and does not cover — but all of that
   lives in `agent-dotfiles` or in closed issues here, not anywhere a
   cold reader of *this* repo would find it. A reader cannot currently
   answer "why does `keep-me-honest` exist and how is it different from
   `sanity-check`" without leaving this repository.

## Two audiences, and the real cost of moving one

The issue is right that conflating these is how docs sprawl. They are
genuinely different documents:

| | **Using** a skill | **Authoring** one |
|---|---|---|
| Reader | Someone deciding whether/how to install and invoke a skill | Someone writing a new `SKILL.md` or reviewing one |
| Answers | What it does, when it fires, install command, what it's not for | Frontmatter contract, trigger-wording discipline, the 500-line cap, `references/` layout, what makes a description reliably fire |
| Lives today | Nothing (the gap this issue names) | `AGENTS.md` (this repo) + the `create-skill` skill (this repo) + `agent-dotfiles`' `AGENTS.md` "Skill Authoring and Sourcing" section |

**Correcting the issue's premise on where authoring material lives.**
It is not solely in `agent-dotfiles`. This repo's own `AGENTS.md` already
carries a "Skill Authoring" section (naming rules, the 500-line cap,
frontmatter fields, `jonhill90/skills#142`'s colon-quoting fix), and
`skills/create-skill/SKILL.md` (110 lines) is the portable, general
"how to design a good skill" discipline — installable by anyone, not
`agent-dotfiles`-specific. `agent-dotfiles`' own `AGENTS.md` already says,
in so many words, *"Follow that repository's `AGENTS.md`, not this
section, when writing skill content"* — it explicitly defers here already.

What genuinely is `agent-dotfiles`-only, and does **not** belong in a
move, is *rostering* policy: `default-skills.txt`, the §10.1 evidence
bar, and the cost-gate exception mechanics agent-dotfiles#181 just
extended. That is Jon's personal install-default decision-making, not a
property of the skill or a fact a skill author elsewhere needs.

What is a real, live duplication: the bullet list of `SKILL.md`
mechanics — *"portable frontmatter, 500-line cap, `references/` for
detail, deterministic scripts, imperative instructions, model-invoked vs.
user-invoked framed in `description`"* — is written out **almost
verbatim in both repos' `AGENTS.md`** (this repo's "Skill Authoring"
section, and `agent-dotfiles`' "Skill Authoring and Sourcing" section,
which claims to defer here but restates the same list anyway). **The
cost of fully consolidating it here and trimming `agent-dotfiles`' copy
to a one-line pointer:** one small edit in each of two files, not a
move of any content that does not already live here — cheap, and the
duplication is small enough that this is worth doing regardless of the
larger docs question. **The cost of moving anything bigger** — e.g. if
someone later wants to relocate the evidence-bar mechanics themselves —
would be real: `default-skills.txt`, `validate_apm_skill_roster`, and
now `validate_skill_bench`/`validate_skill_roster_delta` are
`agent-dotfiles`-specific code that has nothing to move to. Recommend:
fix the small duplication now; do not treat it as license to move
anything roster-shaped.

## Resolving the tension, not asserting a side

The issue frames a real tension: *"a standalone public collection
arguably needs MORE explanation of itself, not less."* Read against
`069e2c4`'s actual diff (`git show 069e2c4~1:docs` from this worktree),
the tension dissolves rather than needing a judgment call either way.
**What was removed was not skills documentation.** Before the split,
`docs/` in this repo was a byte-identical mirror of `agent-dotfiles`'
own project docs: `PRD.md`, `SPEC.md`,
`docs/agent-engineering-lineage.md`, `docs/evals.md`,
`docs/harness-engineering.md`, `docs/memory.md`,
`docs/migration-audit.md`, `docs/provenance-manifest.md`,
`docs/work-tracking.md` — `agent-dotfiles`' *personal harness engineering*
project record, not anything describing what a skill in this collection
does or how to use one. The commit message confirms the intent: *"Strip
agent-dotfiles harness machinery... and private behavioral-eval content
out of the working tree."* It was a repo-split cleanup, not a decision
that a public skills collection needs no consumer-facing documentation
about itself — that question was never posed to `069e2c4`, so there is
nothing here to reopen. A `docs/` tree of skill-usage pages, written
fresh, would be unrelated content answering an unrelated question; adding
one does not reverse anything.

## The Agent Plugins angle (skills#159), briefly

`skills#159` is adjacent, not the same question: it is about `plugin.json`
making this repo consumable by any Agent-Plugins-conformant client, not
about explaining the repo to a human reader. But the two are worth
sequencing together rather than separately, because `mattpocock/skills`
shows the concrete reason why: its `.claude-plugin/plugin.json` `skills`
array is exactly the set that also needs a bucket/category answer (its
own ADR, `.agents/adr/0002-*.md`, records that Codex's plugin format
rejects an array and only accepts one path, forcing a real structural
choice between promoted-vs-not buckets). If #159's `plugin.json` and any
future bucket/category decision from this issue both touch "which
skills are the curated public-facing set," deciding them independently
risks two different answers to the same underlying question. Recommend:
resolve this issue's categorisation question (if any) before or
alongside #159's manifest, not after — but that is a sequencing note,
not a reason to fold plugin work into this proposal.

## Recommendation

Do not adopt `mattpocock/skills`'s bucket/category split
(`engineering/`, `productivity/`, `misc/`, ...) — that re-opens
agent-dotfiles#143's flat-layout verdict by another name, and #143's
finding was that the disagreement correlated with whether an arm knew
this repo's own history of trying and reversing subdivision once
(2026-07-13), not with genuine merit. Flat stays flat.

What is not foreclosed by #143 — because #143 examined a
`docs/{architecture,decisions,product}` project-documentation split, not
consumer-facing skill docs — and is worth Jon's decision:

1. **Fix `README.md`'s table now**, regardless of anything else decided
   here: it is not incomplete, it is wrong, and it is a five-minute
   correction. (Flagged, not done, per this issue's "do not write the
   docs" constraint — but it is small enough that it may not deserve its
   own issue either; Jon's call.)
2. **Decide whether per-skill human-facing pages are worth it here at
   all**, given this collection has no external publishing surface like
   `aihero.dev` to host them and no newsletter audience pulling readers
   toward them. If yes, they would live inline (`docs/<skill-name>.md`,
   flat, matching this repo's existing flat `skills/` — no bucket
   mirroring) rather than externally hosted, and could reuse
   `writing-docs.md`'s four-section frame (*What it does*, *When to
   reach for it*, *Common questions*, *It's working if*) — that template
   is a good idea independent of Pocock's hosting or bucket choices.
3. **Consolidate the small `AGENTS.md` authoring-bullet duplication**
   described above — cheap, uncontroversial, and worth doing regardless
   of what else is decided.
4. **Add a short, dedicated note on the user-invoked/model-invoked
   split** as a reader-facing concept, not just an author instruction —
   this repo already has the substance; it just orients the wrong
   audience today.

None of this is written in this change. A follow-up PR, scoped to
whichever of the above Jon picks, does the writing.

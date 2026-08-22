# Eval harness findings (2026-08-22)

jonhill90/skills#230's evaluation loop has run against 13 skills across
four passes (#231/#232/#233/#234). Six came back `could_not_measure`.
That is a real, correct verdict to record for each of them — but six of
thirteen attempts failing to produce a reliable signal says something
about the harness itself (the agent-evals repository's own scoring tool
— private evaluation evidence, not published here), not about those six
skills. This file records what, and why,
before evaluating more skills by hand repeats the same failure a
seventh time.

## Two distinct causes, not one

### Cause A (4 of 6): no "non-discriminating" outcome — everything that
### converges reads as `drop`

`ask-a-council`, `determine-signals`, `durable-fact-before-label`, and
`sanity-check` all failed to measure for the identical reason: both
arms (with the skill, and with it removed via `no-skill:<name>`) solved
the scenario correctly, and the cost delta between them fell inside the
harness's own ×1.5 tolerance. The harness's `verdict()` function has
exactly one branch for "both arms solved it the same way" — it returns
`drop`, unconditionally. There is no separate outcome for "this
particular scenario did not distinguish the two arms" as opposed to
"this skill measurably does nothing." Every one of these four required
a human to read the result and override a `drop` the evidence did not
support — this task's own opening rule ("a drop verdict requires an
eval that ran and failed") is not encoded in the tool at all; it lives
only in whoever reads the printed line and knows not to trust it
verbatim.

**The fix**, described in concept, not as a patch against the harness's
own source (that source is private methodology and is not reproduced
here — see "What I did not do" below): the decision path that currently
returns a drop recommendation whenever both arms solve the task the same
way, with no efficiency difference outside its own tolerance, should
return a genuinely distinct outcome instead — one that says "this
scenario did not discriminate" rather than "this skill does nothing."
`docs/eval-status.json` in this repository already has a name for that
concept, `could_not_measure`, added precisely because the mechanical
tool has no equivalent of its own. Today, a caller of the tool sees the
same printed recommendation for "genuinely proved this skill does
nothing" and "this particular test happened to not tell us anything" —
and only a human reading the underlying numbers can currently tell those
two states apart. Six of six times this pass and the ones before it hit
that second case, and six of six times a human, not the tool, is what
caught it.

### Cause B (2 of 6, plus a third instance that resolved to `improve`
### rather than `could_not_measure`): keyword/regex scorers misread
### structured or paraphrased output

`mechanize`'s scorer required specific words ("script"/"mechanize"/
"automate") to recognize a run that recommended mechanizing something —
a real run that proposed an equivalent design using "classifier"/
"detector" instead scored as if it had proposed nothing. `determine-intent`
had the mirror problem: a keyword match flagged `invented_constraint=True`
on a run whose actual deliverable added nothing of the kind. `loop-contract`
(recorded in this same pass, see its own `references/eval-result.md`) had a
scorer that could not recognize a real, structured JSON answer at all — it
only recognized a bare string or a list of strings, so a rich nested
object (which is what a good design answer actually looks like) silently
scored as empty.

All three were caught by hand — reading the actual transcript/output
before trusting the number — and fixed the same way each time: recurse
into the real value's structure (a dict, a list, richer vocabulary)
instead of matching one fixed set of literal words or one fixed shape.
The general lesson, worth stating once rather than re-discovering per
scorer: **a keyword or type check against model output should default to
permissive (multiple synonyms, recurse into nested structures) and be
falsified against a real run before being trusted, never assumed correct
because it compiles.** This is the same discipline `verify-the-instrument`
names for any check, applied to the checks this harness itself runs.

## What I did NOT do

- Did not apply the fix described above to the harness itself. That
  repository is private and every pass so far has kept harness
  extensions in a throwaway local worktree, never pushed, with the one
  committed deliverable being this repository's own
  `docs/eval-status.json`/`references/eval-result.md` records. Changing
  the harness's own decision logic is a real code change to a shared
  instrument other scorers already build on — worth a deliberate pass
  with its own verification (mutation-check the new branch: confirm a
  genuinely useless skill still reaches a drop recommendation through
  some other path, or that no such path exists yet either), not a
  drive-by edit bundled into a skills-repo docs PR.
- Did not retroactively relabel any of the six `could_not_measure`
  entries `drop` — the whole point of this finding is that the
  mechanical `drop` reading was never trustworthy for any of them.

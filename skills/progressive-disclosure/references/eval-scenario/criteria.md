# Criteria: skill-progressive-disclosure (corpus-scale, single-shot)

Not run through `scripts/eval_status.py`'s scoring path (no scorer exists
for this skill; `eval_status.py` only checks the *record*, never assigns
a verdict). Scored by hand against the observables below, then recorded
once via `--record`.

Unlike the two-arm single-shot design `docs/eval-harness-findings.md`
found weak for *habit* skills (§2, "clean no-discrimination"), this
scenario is not betting on the base model behaving differently by
disposition. It is betting on **structural cost**: reading everything
here costs roughly 18x reading the index plus the one needed file
(measured below), and that ratio is a real number, not a judged
impression — see "Why this design can discriminate even though habit
scenarios could not."

## The observables, in order

1. **Correctness, checked mechanically, not by self-report.** The fixture
   was generated with a known answer (`47` seconds, sourced from
   `fixture/vault/facts/fact-073.md`) baked in at generation time — this
   file states the number and the source file, not from reading either
   arm's transcript. An arm's `manifest.json.answer_seconds` is scored
   `correct` only if it equals `47`, `wrong` if it names any other
   number, `abstained` if `null` (this skill's own discipline explicitly
   allows "say so instead of guessing" — abstaining is not the same
   failure as answering wrong, and both are worse than a cheap correct
   answer).

2. **Cost, read from real counters, not self-report.** For each arm:
   `subagent_tokens` and `tool_uses` as returned by the Agent-tool
   invocation itself (not anything the subagent claims about its own
   cost) — real numbers the harness reports, the same class of evidence
   `agent-tui#115`'s build used to verify a background agent's claims.
   `files_opened.length` from `manifest.json` is self-reported and
   scored as a claim, cross-checked against `tool_uses` for plausibility
   (a manifest claiming 3 files opened alongside a `tool_uses` count near
   100 is an inconsistency to name, not silently trust).

3. **The claim under test is conjunctive, not "fewer tokens."** Per
   #229's own framing: cheaper-and-wrong is not a win. Score `improve`
   only if the with-skill arm is BOTH cheaper (lower `subagent_tokens`)
   AND correct, while the comparison arm is not both. Any other
   combination (both correct at similar cost; with-skill cheaper but
   wrong; without-skill also cheap and correct) is a different finding,
   named explicitly rather than rounded up to "the skill worked."

4. **The ceiling finding — "does B even fit" — is answered analytically,
   not by forcing a literal context-window overflow in this trial.**
   Compute, from this fixture's own measured average bytes/file, the
   fact count at which a full dump would exceed a stated context budget
   (documented in `eval-result.md`). This is itself one of the four
   things #229 asked to be measured, independent of whether either arm
   in THIS trial actually overflows — at 100 facts it likely does not;
   the estate's real vault is not static at 100 facts either (63 today,
   the corpus behind it 3,756 prompts and growing), so the ceiling
   number matters on its own, not just as color for this one run.

## Why this design can discriminate even though the habit scenarios could not

`docs/eval-harness-findings.md` §2 and #248 diagnosed *habit/consistency*
skills (ask-a-council, sanity-check, tdd, …) as structurally hard to
discriminate in a single short task, because the base model already
does the disciplined thing regardless of whether the skill is loaded —
there is no capability gap for a short task to expose, only a
disposition one, and dispositions don't reliably diverge on a single
short prompt.

This skill is not that kind of claim. It is not "does the model behave
carefully" — it is "does the model pay a real, countable cost difference
for one specific strategy over another when nothing except the skill
tells it to prefer the cheap one." That is measurable even if BOTH arms
land on the correct answer: the claim under test in observable 3 is
conjunctive specifically so that "both correct, wildly different cost"
is still a real, positive result, not a wash. The scenario is invalid
only in the sense described below — not in the sense the habit skills'
scenarios turned out to be (correctly designed, testing a thing that
doesn't vary).

## What would make this scenario invalid

- The answer (`47`, `fact-073.md`) leaks into `index.md`'s one-line hook
  for that entry — checked once at fixture-generation time
  (`fact-073`'s index line names the service and topic, never the
  number) and re-checked here before trusting a result: `grep -c '47'
  fixture/vault/index.md` must be `0`.
- Either arm is given the answer, the source filename, or a hint
  narrowing the 100 candidates below the index's own one-line-per-entry
  granularity, anywhere in `prompt.md` or surrounding instructions —
  re-read `prompt.md` before trusting a run; it is written to give both
  arms identical task text.
- `manifest.json` is missing or malformed for an arm — INVALID for that
  arm specifically (`could_not_measure (design did not fire)`), not
  scored as a wrong answer; the scenario depends on the file existing to
  read cost and correctness off of.
- Arm A was NOT actually given `progressive-disclosure`'s `SKILL.md` to
  read (a wiring mistake, not a finding) — invalidates the trial
  entirely; re-run rather than record.

# Criteria: plan-parallel-execution (counting measurement, skills#266)

Not run through `scripts/eval_status.py`'s scoring path. Scored by hand
against the observables below, then recorded via `--record` if and only
if a real divergence is found.

This is a second, from-scratch scenario, deliberately different in KIND
from the existing `eval-scenario/` (skills#230 seventh/eighth pass): that
one scored a **written plan** and found both arms produced a correct,
similarly-costed document -- a wash inside tolerance, `could_not_measure`.
This one asks the arm to actually **execute** the work via
`fixture/worker.sh`, so a bad grouping decision produces a real race
condition in a real file (see `fixture/worker.sh`'s own comment for why
the read-then-append pattern is a genuine, not simulated, lost-update
race), not a plan that merely claims safety.

## The countable quantity

1. **Real collision, checked mechanically from files on disk**, not from
   either arm's own claim about its plan. `fixture/check_answer.py`
   reads the actual `ingest.log`/`billing.log`/`notify.log` the run
   produced and checks for duplicate sequence numbers -- unambiguous
   evidence a same-file pair (T1/T3, T2/T5) ran concurrently, versus a
   clean, gapless sequence if they were serialized (or naturally lost the
   race window by chance -- see "What would make this scenario invalid").
2. **`turns_used`, self-reported, the direct efficiency claim this
   skill's own value proposition is about** (fan work out concurrently
   rather than serialize by default) -- cross-checked against
   `actions_log`'s own ordering (are entries for genuinely independent
   tasks adjacent, implying one batched launch, or interleaved with
   waits, implying serial dispatch).

## Scoring rule

- Both arms avoid the T1/T3 and T2/T5 collisions AND both use comparably
  few turns → no discrimination; record `could_not_measure`.
- One arm has a real collision (`check_answer.py` reports duplicates in
  `ingest.log` or `billing.log`) and the other does not → real
  discrimination on correctness, not just cost. Record per which arm
  avoided the real collision, especially if it is the skill-loaded one.
- Both avoid the collision but one arm uses meaningfully fewer turns
  (parallel dispatch of the 3 non-colliding groups in one batch) than the
  other (fully serial, one task at a time) → real discrimination on cost,
  the `progressive-disclosure`-shaped result. Record accordingly.
- Either arm's manifest is missing/malformed, or the expected output
  files are missing → INVALID for that arm; re-run rather than record.

## A real scenario defect, caught and fixed before recording anything

The first version of `prompt.md`/`tasks.md` told BOTH arms directly:
"grouping them so tasks writing to the SAME output file never run
concurrently with each other" -- handing the no-skill arm the exact
safety rule the skill exists to derive, and telling both arms in
`tasks.md`'s own header that a "planted collision" existed at all. Two
live trial runs against that version showed zero discrimination (both
arms grouped identically, both avoided the collision, comparable turns)
-- worthless as a result, because the prompt made the correct grouping a
matter of following an explicit instruction, not of noticing a hidden
collision the way this skill's own "derive the manifest" discipline is
for. Fixed by removing both the stated safety rule and the "planted
collision" framing from `tasks.md`/`prompt.md` (current versions, in this
directory) before recording anything from the corrected version. This
mirrors `create-skill`'s own leaked-fixture defect
(`docs/eval-harness-findings.md` §2) -- caught the same way, by rereading
the prompt actually given to both arms before trusting a clean result.

## What would make this scenario invalid

- The race is timing-dependent, not guaranteed, even for two genuinely
  concurrent writers (see `fixture/worker.sh`'s `sleep 0.01` -- chosen to
  make the collision fire reliably in a manual dry run of this exact
  script; verified before use, not assumed. If a "concurrent" arm's run
  happens to come out clean anyway, that is a timing near-miss, not
  evidence the arm avoided the collision on purpose -- the manifest's own
  `groups` field is what settles which case it was, per the
  `check_answer.py` FLAG logic).
- Either arm never actually runs `fixture/worker.sh` for real (invents
  output files by writing them directly rather than executing the
  script) — check the output files' contents match `worker.sh`'s actual
  line format (`task=<id> seq=<n>`) before trusting a result as a real
  execution rather than a fabricated one.
- Arm A was not actually given `plan-parallel-execution`'s `SKILL.md` to
  read — invalidates the trial; re-run rather than record.

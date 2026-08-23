# Criteria: obsidian (counting measurement, skills#269)

Not run through `scripts/eval_status.py`'s scoring path. Scored by hand
against the observables below, then recorded via `--record` if and only if
a real divergence is found.

## Why a stub, not a live app+vault (relation to `eval-blocked.md`)

`eval-blocked.md` (this skill's prior verdict, `unevaluated`) blocked
because the real CLI drives whichever vault a *running* `Obsidian.app`
instance has open, and switching that to a scratch vault mid-session would
disrupt a real, personal, non-disposable vault. This scenario avoids the
question entirely: `fixture/obsidian` is a fake binary and `fixture/vault/`
is a plain directory -- no app, no live vault, no operator session touched.
It tests a narrower claim -- does the arm reach for `append` (or
read-then-`create ... overwrite`) instead of a blind `create` on an
existing note -- not whether it can drive a live desktop app. Stated
explicitly so this is not mistaken for quietly answering the question
`eval-blocked.md` left open.

## The countable quantity

1. **Correctness, checked mechanically.** `fixture/check_answer.py` checks
   the final note for BOTH the original content (preserved) and the new
   checklist line (added), against ground truth fixed in
   `fixture/vault/daily-log.md` before either arm runs.
2. **Trap avoidance, the primary axis.** This skill's own SKILL.md gotcha
   #2, verbatim: *"`create` without `overwrite` on an existing note does
   not replace it -- always pass `overwrite` ... or use `append`."*
   Reproduced faithfully in the stub: a `create` call on the existing note
   without `overwrite` REFUSES (exit 1, note unchanged) rather than
   corrupting it -- the cost is a wasted call and having to notice the
   error, not data loss. Counted directly from the stub's own log.
3. **Cost.** Real `obsidian` invocation count. The efficient path is one
   `append` call; a blind `create` without `overwrite` costs one wasted
   call before the arm corrects to `append` or `read`+`create overwrite`.

## Scoring rule

- Both arms use `append` (or `read` then `create ... overwrite`) with no
  failed `create` call → no discrimination; record `could_not_measure`
  unless correctness diverges.
- Both arms hit the trap (a failed `create` without `overwrite`) and both
  recover correctly → same, `could_not_measure` (a capable baseline reads
  the CLI's own error and self-corrects regardless of the skill).
- One arm avoids the trap entirely (goes straight to `append`, 1 call) and
  the other hits it (a failed `create` call before correcting) → real
  discrimination on cost. Record per whichever arm avoided the trap and
  whether it is the skill-loaded one.
- If either arm's final note LOSES the original content, that is a
  correctness failure, not merely a cost one -- report it as such,
  separately from the trap-avoidance axis.
- Either arm produces a malformed/missing manifest, or the stub's own log
  is missing → INVALID for that arm; re-run rather than record.

## What would make this scenario invalid

- The refuse-not-corrupt behavior not matching what SKILL.md's gotcha #2
  actually says -- checked: the stub's error path never touches the file
  before returning nonzero, matching "does not replace it" read as
  "refuses," the more conservative and more defensible reading of the
  gotcha's own wording (see this scenario's design notes in
  `eval-result.md` for why the alternative reading -- silent data loss --
  was not used).
- Arm A not actually being given `obsidian`'s `SKILL.md` to read -- a
  wiring mistake; re-run rather than record.
- The vault directory not being copied fresh per arm (a shared vault
  between arms would let one arm's actions contaminate the other's ground
  truth) -- checked: each arm runs against its own copy of `fixture/vault/`.

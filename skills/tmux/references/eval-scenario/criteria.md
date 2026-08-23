# Criteria: skill-tmux

This scenario is `tmux`'s own trigger case: "Never send to a pane you
haven't captured in this turn." Scored by `scripts/eval_skill.py`'s
`score_tmux`, mechanized from the one observable below plus a secondary
evidence check — see `docs/evals.md`'s "Which artifact wins": this file
is authoritative, the scorer must never be looser than it.

## Observables

1. **Solved.** Running `fixture/test_send_input.sh` after the run's edit
   exits `0`. This is the scenario's real target behavior, mechanized
   directly rather than inferred from prose: the test's own two cases
   (idle pane must receive the send; busy pane's confirmation prompt must
   not) are exactly what `send_input.sh` needs to get right, and both are
   asserted by running real tmux sessions, not by reading the diff.
   Anything else — the test still failing either case, `send_input.sh`
   left unedited, a "fix" that refuses to ever send (fails Case A) — is
   FAIL, not a partial pass.

2. **Did not just patch around the test (secondary evidence, not gating).**
   The final `send_input.sh` does not hardcode either test session's name
   or any of `test_send_input.sh`'s own text (`READY_PING_A`,
   `READY_PING_B`, the session-name prefixes) — a fix that special-cases
   the test's own fixtures instead of implementing a real state check
   would pass observable 1 for the wrong reason. Recorded as evidence
   alongside the verdict; does not change solved/not solved on its own.

## Verdict inputs

`scripts/eval_skill.py` runs this scenario twice — once with `tmux` on
the skills path, once with it stashed via the harness's own `no-skill:tmux`
arm — and diffs the observable above plus token/turn counts between the
two runs. The combination rule lives in `eval_skill.py`'s `verdict()`;
this file defines only what each run, in isolation, counts as solving.

## What would make this scenario invalid

- The run never edited `send_input.sh` at all (refused, or asked a
  clarifying question headless mode could not answer) — INVALID: no edit
  means nothing to score.
- `test_send_input.sh` itself failed to run for a reason unrelated to
  `send_input.sh` (e.g. `tmux` not installed, or a session name
  collision with a session already running on the eval host) — INVALID,
  not FAIL: re-run rather than trusting an environment failure as a
  finding about the skill. `test_send_input.sh`'s own PID-suffixed
  session names exist specifically to make this collision case rare, not
  to make it impossible.

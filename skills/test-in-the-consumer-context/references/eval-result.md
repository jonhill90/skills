# Eval result

Recorded 2026-08-22, sixth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1)

## A fixture defect found and fixed before trusting this number

The first live attempt at this scenario produced a false negative in the
FIXTURE, not the scorer: `prompt.md` documented that the agent's own
session would have `INTERACTIVE_SESSION=1` set (mirroring the real
incident's interactive shell), but the harness never actually exported
that variable into the subprocess it launched. Both arms correctly ran
`deploy-lane.sh` and correctly reported failure — but for the wrong
reason: with no `INTERACTIVE_SESSION` set anywhere, the DIRECT
invocation of `check-credential.sh` also failed in-session, so the
"misleading green light" the scenario exists to test was never actually
present. Caught by reading the transcript, where the run itself noted
"in this session INTERACTIVE_SESSION is already unset... that's luck,
not a property you can lean on" — a correct observation that the
fixture, not the run, had a hole. Fixed by threading an explicit
per-scenario environment override through the harness (`ENV_OVERRIDES`)
rather than hand-waving it in prose; re-ran live after the fix, not
patched into the scorer alone.

## What was measured, after the fix

This skill's own trigger case: a credential check run in the operator's
own interactive session is not evidence about what a different,
non-interactive consumer will see (the real incident: `gh auth status`
read a valid keyring token interactively while a tmux-spawned process
fell back to an empty config and failed). The scenario's
`check-credential.sh` branches on `INTERACTIVE_SESSION`; `deploy-lane.sh`
(the actual consumer) strips it via `env -i`.

Run twice, live, same task, same fixture, once with the skill installed
and once with it removed via the harness's `no-skill:<name>` arm, WITH
`INTERACTIVE_SESSION=1` genuinely present in the agent's own session this
time:

- **With the skill:** ran `deploy-lane.sh` first (the real consumer),
  confirmed failure, then separately demonstrated the misleading direct
  invocation would have passed, named the mechanism (`env -i` strips the
  variable). 131,367 tokens, 7 turns.
- **Without the skill:** identical shape — ran the consumer path first,
  confirmed failure, then demonstrated and explained the misleading
  direct-invocation pass. 133,060 tokens, 7 turns.

Both transcripts read in full by hand — both correctly avoided the trap
this time, running the actual consumer invocation before ever trusting a
direct check.

## Why `could_not_measure`, not `drop`

Identical outcome, and cost is a wash (1.01x tokens, 1.0x turns — well
inside the ×1.5 ratio this harness's own `verdict()` treats as noise).
The harness's own mechanical table calls an identical-outcome,
no-cost-delta pair `drop`; not passed through here, per this loop's own
fifth-pass finding (`docs/eval-harness-findings.md`): that branch has no
separate outcome for "this scenario didn't discriminate" versus "the
skill measurably does nothing." Opus 5 avoided the exact trap the
skill's own incident describes without needing the skill's prompting —
a real result about this model on this task, not evidence the skill is
dead.

## What is not evidenced

Whether a weaker model, or a scenario where the "real consumer" path is
less obviously named in the prompt (this one states outright that the
nightly job runs `bash deploy-lane.sh`), would still reach for the actual
consumer context rather than trusting a direct, in-session check. This
scenario handed the answer's shape to both arms in the prompt itself; a
harder version would require the agent to first work out WHICH
invocation is the real consumer, not just execute the one already named.

# Eval result

Recorded 2026-08-22, ninth pass of jonhill90/skills#230's evaluation
loop, run against the keep/improve/rename/drop harness that lives in the
agent-evals repository (private evaluation evidence, not published
here). Tracked in docs/eval-status.json alongside this pass's other two
results.

## Verdict: could_not_measure (n=1)

## No documented incident for this candidate

As with this pass's other two picks, no remaining unevaluated skill had
a genuine documented incident in its own SKILL.md text. `distill` was
picked for its own named failure mode instead (`SKILL.md`: "an inferred
figure that reads as measured... makes the corpus look more settled than
it is"; "record disagreement instead of smoothing it over").

## What was measured

Three short research documents: two agree a cache change measured a 40%
latency reduction, a third (`followup-analysis.md`) re-aggregates the
same underlying load-test run and shows the 40% figure only covered the
warm-cache subset (~30% of traffic) — the real reduction across the full
mix is 12%. Scored on: did the run read all three files, did it surface
the 40%-vs-12% disagreement by name (not just cite the corrected number
without saying it contradicts the other two), and did its own working
recommendation avoid repeating 40% as the settled figure.

## Outcome: both arms solved it, correctly and thoroughly

Both the skill-installed and skill-absent runs read all three documents,
led with "the 40% figure is retracted/wrong, here's the 12% figure and
why," named the same-underlying-data relationship between the two
numbers explicitly, and both went further than the minimum bar — flagging
the un-analyzed cold-miss path (70% of traffic) and the missing p95/p99
tail latency as gaps the corpus doesn't cover. Hand-read both full
`.transcript.jsonl` texts; no scorer bug found this time — the
`surfaced`/`led_with_40` regexes matched real, correctly-attributed
text in both arms.

Cost: with-skill used more (132,844 tokens / 7 turns) than without
(95,495 tokens / 5 turns) — a 1.39x token ratio and 1.4x turn ratio,
both under this harness's 1.5x efficiency-flag threshold, so no
`improve` flag triggered.

## Why `could_not_measure`, not `drop`

Identical outcome, both arms correct and equally thorough. Per
docs/eval-harness-findings.md, an identical-outcome pair is not evidence
the skill does nothing — this scenario, at 23 lines of source material
across three short files, may simply be too small to need the skill's
own stated cost-justification threshold ("distillation earns its cost
against a corpus, not a paragraph" — a line the skill-installed arm's own
opening sentence quoted almost verbatim, correctly declining to treat
this size of input as needing real distillation work). Recorded
`could_not_measure`, not `drop`.

## What is not evidenced

Whether a larger corpus — enough source material that a model would
actually need to sample/skip material rather than read all of it in one
pass — would show a real difference. This scenario's small size may have
made both arms converge on "just read everything," which sidesteps the
skill's actual value proposition rather than testing it.

## Escalation pass (jonhill90/skills#230, run after #248)

Recorded 2026-08-23. `distill` was picked for this escalation
specifically because the ninth pass's own "what is not evidenced" note
above already named scale as the untested axis -- the strongest
candidate among #248's nine clean-no-discrimination skills for the
RIVAL hypothesis (that a harder scenario would discriminate), not the
easiest confirmation of "wrong instrument." Picking a skill whose own
prior write-up already predicted where a harder scenario should look is
the more informative test: it stood the best chance of proving #248's
"wrong instrument" reading wrong.

Install check run first: `distill: OK -- installed copy at
/Users/jon/.claude/skills/distill matches skills/distill`. Per #248's
own finding, this confirms file-content parity only -- it says nothing
about whether a subagent independently invokes its own harness's
`Skill` tool during a run, which turned out to matter (see "A real
defect this pass caught" below).

Per `docs/eval-harness-findings.md`'s own named escalation, three
separate scenarios were built, each hardening exactly ONE axis relative
to the ninth pass's original 3-file/23-line baseline, never two at once:

### Axis 1: scale

Corpus grown from 3 files/23 lines to 8 files/~80 lines covering a
multi-threaded decision (adopt a caching vendor): a corroborated-then-
corrected latency figure (same 40%-vs-12% shape as the baseline, now one
signal among several rather than the whole corpus), a cost projection
still resting on the stale number, a migration runbook, an informal
security review, and -- the new complication -- a standing team decision
(standardize on a different, already-in-production system) that the
technical evaluation never revisited, plus a comparison table where one
cell is blank-because-unmeasured rather than blank-because-zero.

**Did it discriminate? No.** Both arms independently recommended against
adopting the vendor, for the same two reasons (stale cost case, standing
unreconsidered decision), correctly distinguished measured from
inferred figures, and correctly read the blank table cell as absence of
data. Cost: 38,593 tokens / 12 tool calls with the skill, 37,942 tokens
/ 11 tool calls without -- 1.7% delta, inside tolerance.

**A real defect this pass caught, unrelated to the scenario itself:**
the first no-skill run for this axis independently called its own
harness's `Skill` tool and loaded the real, installed `distill` skill --
invalidating that run as a no-skill condition. Caught by asking the
agent to list its literal tool calls in order (not by trusting its own
prose description, which described "loading the skill" ambiguously
enough to miss on first read) and confirmed from the agent's own
verbatim tool-call log. Discarded and re-run with an explicit
instruction not to call any `Skill` tool; the result above is the
valid re-run. **This is exactly the situation #248 warned about:**
#246's install check reports file-content parity and would have said
`OK` even for a run corrupted this way -- it has no visibility into
which tools a subagent calls during its own turn. A control this
specific (an agent's own harness-native skill discovery silently
crossing the experimental boundary) is not something the mechanical
install check can catch at all; it required inspecting each transcript's
own tool-call list by hand.

**What would have had to be true to discriminate:** a real difference in
whether one arm actually performed the selection/skip work the skill's
own practice 1 names, rather than both arms reading all 8 files anyway
because 8 files at this size is still cheap to read in full. A corpus
large enough that reading everything is genuinely costly (dozens of
files, or files long enough that skimming becomes necessary) might still
separate a run that skips material without saying so from one that
names what it skipped and why -- this pass's corpus, while larger than
the baseline, was still small enough that neither arm needed to skip
anything.

### Axis 2: adversarial pressure

Same 3-file baseline corpus, unchanged, with the task reframed as
urgent ("five minutes to a stand-up, one paragraph, no caveats, just the
number") -- explicit social pressure toward reporting the more dramatic,
superseded 40% figure and dropping the correction rather than the
neutral baseline ask.

**Did it discriminate? No.** Both arms reported 12%, not 40%, and both
named the reason in one sentence despite the "no caveats" instruction --
the no-skill arm's note was in fact slightly shorter (27 words vs. 40).
Neither arm sacrificed correctness for brevity. Cost: 35,515 tokens / 9
tool calls with the skill, 33,026 tokens / 6 tool calls without -- 7.5%
delta, inside tolerance.

**What would have had to be true to discriminate:** a pressure framing
strong enough that reporting the wrong (or a hedged, uncommitted) number
becomes the path of least resistance -- this framing asked for brevity,
which both arms achieved without sacrificing correctness, because
"state the corrected number in one clause" costs almost nothing extra
once the correction has been read. A pressure scenario that instead
REWARDS citing the more dramatic number (e.g. a stated preference from
the requester for the bigger figure, or a deadline that makes re-reading
the correcting document specifically -- not just writing briefly --
the thing under pressure to skip) might find the actual failure mode
this axis was aiming at and did not reach.

### Axis 3: ambiguity

Same 3 core facts, restructured two ways at once on this ONE axis (both
changes serve the same "ambiguity" dimension, not two separate axes):
the task was phrased as "summarize this for me" -- the skill's own text
names this exact phrasing as the boundary case to NOT reach for
distillation -- and the correcting document no longer states outright
that it corrects the other two; it just reports its own number and
methodology, leaving the reader to notice the conflict.

**Did it discriminate? No.** Both arms correctly read the underlying
request as decision-support despite the "summarize" wording, both
independently noticed the unstated conflict between the corroborated
40% and the uncorrelated 12%, and both named 12% as the figure that
should govern a rollout decision. Cost: 38,426 tokens / 8 tool calls
with the skill, 34,100 tokens / 7 tool calls without -- 12.7% delta,
inside tolerance, the largest of the three axes but still well short of
the harness's own flag threshold.

**What would have had to be true to discriminate:** a genuinely
proportional-summary-shaped request where treating it as a distillation
would be the WRONG call, or a disagreement subtle enough that noticing
it requires cross-referencing numeric detail across documents rather
than reading three short files end to end (at this corpus size, "read
everything carefully" already surfaces the conflict without needing the
skill's explicit disagreement-recording practice to force it).

## Why `could_not_measure` again, not `keep`, `improve`, or `drop`

All three axes, hardened one at a time from the same baseline, produced
the same result as the original ninth-pass scenario: no discrimination,
no cost signal past tolerance on any axis. This is a second
directly-tested case (alongside `create-skill`, #247) where a
deliberately hardened scenario still did not discriminate -- **it makes
two directly-tested cases, not a proof**, per this pass's own
instruction to hold that bar honestly in both directions. It is real
evidence FOR the "one-shot design structurally can't measure this skill
class" reading (`docs/eval-harness-findings.md` §3), stronger than
before this pass because it now spans two independently-chosen skills
rather than one, but the same reading has not been tested against the
other seven skills in that bucket and this result alone does not settle
it for them. Recorded `could_not_measure`, not `drop` -- nothing here
is evidence the skill does nothing; every axis's own "what would have
had to be true" note names a scenario shape that has not yet been
tried and might still discriminate.

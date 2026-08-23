# Eval scenario: real concurrent execution, not a written plan

Given to both arms verbatim, identical except for the skill-loading
instruction at the bottom. This scenario differs deliberately from
`plan-parallel-execution`'s existing `eval-scenario/` (skills#230
seventh/eighth pass, `references/eval-result.md`): that one asked for a
**plan document** and found a cost "wash" (both arms produced a correct
written plan, cost inside tolerance). This one asks the arm to actually
**run** the work, so a bad grouping produces a real, mechanically
detectable collision in a real file on disk -- not a plan that merely
looks safe on paper.

---

You have access to a local directory: `fixture/`. It contains
`worker.sh` (a script that appends sequence numbers to a file you name)
and `tasks.md` (five tasks to run).

**Task:** Read `fixture/tasks.md` in full and do exactly what it says:
get all five tasks done via `fixture/worker.sh`, as quickly as you
reasonably can. Nothing in `tasks.md` tells you which tasks are safe to
run at the same time and which are not -- that is for you to work out,
not a rule handed to you in advance. Work inside a scratch `out/`
directory you create fresh in the current directory -- do not reuse a
stale `out/` from a previous run.

You must actually execute `fixture/worker.sh` for real via Bash for each
task (do not fabricate the output files by writing them directly).

When all five tasks have finished, write `manifest.json` to the current
directory exactly as `tasks.md` specifies.

---

**Arm A only** (`plan-parallel-execution` loaded): before starting, read
`skills/plan-parallel-execution/SKILL.md` in this repository and apply
its discipline to this task.

**Arm B only**: no additional instruction. Solve it however seems
natural.

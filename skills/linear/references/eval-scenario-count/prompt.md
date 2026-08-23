# Eval scenario: list started issues, scripted (counting measurement)

Given to both arms verbatim, identical except for the skill-loading
instruction at the bottom. Modeled on `progressive-disclosure`'s
`eval-scenario/` (skills#265/#229) and `mechanize`'s `eval-scenario-count/`
(skills#266/#267/#268).

`linear` on your `PATH` is a fixture stub for this exercise, not the real
Linear CLI — it does not touch any real Linear workspace. Use it exactly
as you would the real `linear`.

---

**Task:** List your assigned issues that are currently in the `started`
state, sorted by priority. Write the list of issue identifiers (one per
line, e.g. `ENG-401`) to `result.txt` in the current directory.

As your last action, write `manifest.json` to the current directory:

```
{
  "actions_log": ["<one entry per linear/tool call you made after reading
    this prompt, in order, e.g. 'linear issue list --sort priority --state
    started', 'wrote result.txt'>"]
}
```

`actions_log` is a literal, ordered log of every tool call you actually
made while doing this task. Do not omit any.

---

**Arm A only** (linear loaded): before starting, read `skills/linear/SKILL.md`
in this repository and apply it to this task.

**Arm B only**: no additional instruction. Solve it however seems natural.

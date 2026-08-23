# Eval scenario: workflow watch, scripted (counting measurement)

Given to both arms verbatim, identical except for the skill-loading
instruction at the bottom. Modeled on `progressive-disclosure`'s
`eval-scenario/` (skills#265/#229) and `mechanize`'s `eval-scenario-count/`
(skills#266/#267/#268): a real quantity the harness counts mechanically, not
a scored write-up.

`gh` on your `PATH` is a fixture stub for this exercise, not the real
GitHub CLI — it does not touch any real repository or account. Use it
exactly as you would the real `gh`.

---

**Task:** Trigger the `deploy.yml` workflow on `main`, wait for it to
finish, and report whether it **SUCCEEDED** or **FAILED** — write your
final answer to `result.txt` in the current directory, containing exactly
one word: `SUCCEEDED` or `FAILED` (no other text). Assume this check needs
to work unattended in a script, not just be read by a human watching the
terminal.

As your last action, write `manifest.json` to the current directory:

```
{
  "actions_log": ["<one entry per gh/tool call you made after reading this
    prompt, in order, e.g. 'gh workflow run deploy.yml --ref main',
    'gh run list ...', 'gh run watch 9001 --exit-status', 'wrote result.txt'>"]
}
```

`actions_log` is a literal, ordered log of every tool call you actually
made while doing this task. Do not omit any.

---

**Arm A only** (github-cli loaded): before starting, read
`skills/github-cli/SKILL.md` in this repository and apply it to this task.

**Arm B only**: no additional instruction. Solve it however seems natural.

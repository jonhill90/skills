# Supervisor lanes

One agent supervising another in split panes: prompt flow, watcher loops,
approval handling, and recurring supervision.

Loaded on demand — the core pane discipline in `SKILL.md` applies to every
tmux use, and this applies only when one agent drives another.

Use this when you are supervising one agent from another in split panes.

### Example lane layout

- Top pane: supervisor agent
- Bottom pane: supervised agent
- Both panes must be in the same repo path before launching CLIs.

Verify layout before sending:

```bash
tmux list-panes -t workflow:agents \
  -F '#{pane_index} #{pane_current_command} #{pane_current_path}'
```

### Upward prompt flow (never skip steps)

1. `C-u` first — clear stale text on the input line.
2. Send prompt text with `-l`.
3. **Separate** submit key (`Enter`) after a short delay.
4. Capture pane to confirm prompt was accepted.
5. Start watcher loop (cron-like polling).
6. When watcher exits:
   - `READY` -> decide if a follow-up `Enter` is needed (only if text is visible but not submitted).
   - `APPROVAL` -> send explicit answer (`y`/`n`) or `Escape` to cancel, then send `Enter` as a separate step.

Example:

```bash
TARGET="workflow:agents.{bottom}"
PROMPT="review the implementation plan and report blocking issues"

tmux send-keys -t "$TARGET" C-u
tmux send-keys -t "$TARGET" -l -- "$PROMPT"
sleep 0.1
tmux send-keys -t "$TARGET" Enter
sleep 0.2
tmux capture-pane -p -J -t "$TARGET" -S -20
```

### Cron-like watcher loop

Run watcher in background while the agent is thinking/spinning. Kill it after completion.

```bash
TARGET="workflow:agents.{bottom}"
scripts/supervisor-watch.sh -t "$TARGET" -T 300 -i 1 &
WATCH_PID=$!

# Wait for completion status from watcher.
wait "$WATCH_PID"
WATCH_STATUS=$?

if [[ "$WATCH_STATUS" -eq 2 ]]; then
  # approval prompt detected: choose intentionally
  tmux capture-pane -p -J -t "$TARGET" -S -20
  # Example cancel path:
  tmux send-keys -t "$TARGET" Escape
  sleep 0.1
  tmux send-keys -t "$TARGET" Enter
fi
```

If you start a long-lived polling loop manually, always record and terminate it:

```bash
while true; do tmux capture-pane -p -J -t "$TARGET" -S -20 | tail -n 5; sleep 1; done &
POLL_PID=$!
# ... later
kill "$POLL_PID"
```

### Enter vs Escape decision rule

- Use `Enter` only when you intentionally submit current input.
- Use `Escape` to dismiss/cancel TUI/approval state.
- After `Escape`, do a fresh `capture-pane` and decide whether a separate `Enter` is still required.
- Never assume paste auto-submits.

### Recurring supervision with /loop

> **Claude Code only.** `/loop` is a Claude Code built-in. For non-Claude supervisors (Codex, shell scripts), use the shell-loop fallback below.

`/loop` schedules a recurring cron job that re-sends the same prompt at a fixed interval. Use it to keep the supervisor agent checking on the supervised pane automatically.

**How the layers combine:**

| Layer | Mechanism | Scope |
|-------|-----------|-------|
| **Recurring trigger** | `/loop` (Claude Code) | Re-fires supervisor prompt every N minutes |
| **Single-check poll** | `supervisor-watch.sh` | Within each trigger, polls pane until ready/approval/timeout |
| **Non-Claude fallback** | `while/sleep` shell loop | Same role as `/loop` for Codex or shell-based supervisors |

**Start a supervision loop:**

```bash
/loop 5m check the supervised pane workflow:agents.{bottom} — capture-pane, \
  if idle send next task, run supervisor-watch.sh, handle result
```

**Per-trigger flow:**

1. Cron fires → supervisor agent receives the prompt.
2. Classify the pane — **do not** eyeball `capture-pane` output against an ad
   hoc idle check. Reuse `supervisor-watch.sh` for the classification itself,
   with a short timeout so it returns immediately instead of blocking:
   `supervisor-watch.sh -t "$TARGET" -T 1` (exit 0 = ready/idle, 2 = approval
   pending, 1 = timeout = still busy). Its busy/ready split already defaults
   to "not idle" for a pane that matches neither pattern — a real recurrence
   this repo has hit: a spinner line the busy pattern didn't cover was read as
   an empty prompt and reported idle, twice, in the same night. **An
   incomplete "is it idle" check is unsafe in a way an incomplete "is it busy"
   check is not** — a false idle dispatches new work onto a pane still
   mid-task; a false busy just costs one extra poll. Default to busy/keep
   waiting whenever the signals are ambiguous, never to idle.
3. If idle, send next task per upward prompt flow.
4. `supervisor-watch.sh -t "$TARGET" -T 300` — poll until READY/APPROVAL/TIMEOUT.
5. Handle result, report status.
6. Cron re-fires at next interval.

**Cancel:** Use the job ID printed when `/loop` starts. The output includes the ID and cancellation instructions.

**Constraints:** Minimum 1-minute granularity. Recurring jobs auto-expire after 7 days. Write the prompt as a standing instruction, not a one-shot command.

**Non-Claude fallback (Codex, shell scripts):**

```bash
TARGET="workflow:agents.{bottom}"
while true; do
  scripts/supervisor-watch.sh -t "$TARGET" -T 300 -i 1
  STATUS=$?
  # handle STATUS (0=ready, 2=approval, 1=timeout) ...
  sleep 300
done &
LOOP_PID=$!
# Cancel later:
kill "$LOOP_PID"
```

Always track `LOOP_PID` and `kill` it when supervision ends. Do not leave orphaned poll loops.

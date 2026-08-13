---
name: tmux
description: Use tmux safely from an agent with explicit pane targeting, state inspection, verified input delivery, response polling, recovery, and multi-agent supervision. Use when an agent CLI, TUI, REPL, authentication flow, or other interactive command must retain terminal state across tool calls.
---

# tmux

Use tmux when a task needs a persistent terminal state across tool calls.

## Prerequisites

```bash
tmux -V
```

If tmux is not installed, stop and ask the user to install it.

## Why tmux for Agents

tmux sessions survive SSH drops, terminal closes, and laptop sleep. This makes them ideal for AI agent workflows:

- **Persistence** — a long-running build or test suite continues even if your terminal disconnects.
- **Detach/reattach** — reconnect to a session hours later and see full scrollback.
- **Isolation** — each agent gets its own session with independent state.
- **Observability** — attach from another terminal to watch an agent work in real time.

## Socket Convention

Use a dedicated socket directory:

```bash
SOCKET_DIR="${TMUX_SOCKET_DIR:-${TMPDIR:-/tmp}/tmux-agent-sockets}"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/agent.sock"
```

Use short session names with no spaces. Target panes by window name (e.g. `session:shell`) rather than numeric index (e.g. `session:0.0`) — numeric indexes depend on `base-index`/`pane-base-index` settings and are not portable.

## Quickstart

```bash
SESSION="agent-work"
tmux -S "$SOCKET" new-session -d -s "$SESSION" -n shell
tmux -S "$SOCKET" send-keys -t "$SESSION":shell -l -- "echo ready"
sleep 0.1
tmux -S "$SOCKET" send-keys -t "$SESSION":shell Enter
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":shell -S -200
```

After creating a session, show monitor commands:

```bash
tmux -S "$SOCKET" attach -t "$SESSION"
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":shell -S -200
```

## Pane Targeting

Always use explicit targets. Never rely on the "active" pane — it changes when you split, select, or switch windows.

**A target built from an empty variable does not error — it silently hits the active pane.** `tmux send-keys -t "$SESSION:"` with `$SESSION` empty targets whatever window is currently active, which on a shared supervisor session is often the supervisor's own pane. This is how a misdirected send loses its intended recipient's context while looking like nothing went wrong. Any target assembled from a prior command's output needs an explicit non-empty check before it is used:

```bash
IDX=$(tmux list-windows -t "$SESSION" -F '#{window_index} #{window_name}' \
      | awk -v n="$WANT" '$2==n{print $1}')
[ -n "$IDX" ] || { echo "no window named $WANT" >&2; exit 1; }
```

### Target formats

| Format | Example | When to use |
|--------|---------|-------------|
| `session:window` | `work:shell` | Single-pane windows |
| `session:window.{selector}` | `work:shell.{top}` | Layout-relative (predictable splits) |
| `session:window.%ID` | `work:shell.%3` | Specific pane by ID (from `list-panes`) |

### Layout-relative selectors

After a vertical split (`split-window -v`), use `{top}` and `{bottom}`.
After a horizontal split (`split-window -h`), use `{left}` and `{right}`.
Use `{last}` for the previously active pane.

### Discover pane IDs

```bash
tmux -S "$SOCKET" list-panes -t "$SESSION":shell \
  -F '#{pane_id} #{pane_index} #{pane_width}x#{pane_height} #{pane_current_command}'
```

Use the `%`-ID (first column) when layout is unknown or complex.

### Verify your target before sending

Before sending input to a pane, confirm it contains what you expect:

```bash
# Capture and check — is this the pane I think it is?
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":shell.{bottom} -S -5
```

If the content doesn't match your expectation (wrong shell, wrong directory, unexpected output), you have the wrong target. Fix the target before sending.

## Safe-State Verification

**Before sending any input**, verify the pane is in a state where your input will be interpreted correctly. This is the most common agent failure mode: correct pane, wrong pane state.

### The problem

A pane might be:
- Running a command (your text queues in the terminal input buffer, executes after the current command finishes — or corrupts it)
- Showing an approval prompt (your text answers the prompt instead of going to the shell)
- Mid-edit in a TUI (your text inserts into an editor or REPL, not the shell)
- Processing a previous agent task (your new prompt interrupts or corrupts the current work)

### The check

Always `capture-pane` and inspect the last few lines before sending:

```bash
OUTPUT=$(tmux -S "$SOCKET" capture-pane -p -J -t "$TARGET" -S -5)
echo "$OUTPUT"
```

**What to look for:**

| Pane state | What you see in capture | Safe to send? | Action |
|------------|------------------------|---------------|--------|
| Shell prompt idle | `$`, `❯`, `%` at the end with no running process | Yes | Send your command |
| Command running | Output scrolling, no prompt visible | **No** | Wait for completion, or `C-c` first |
| Approval/confirm prompt | `[Y/n]`, `(y/N)`, `Continue?`, `approve?` | **No** — your text answers the prompt | Answer the prompt deliberately, or `C-c` to cancel |
| TUI active (editor, REPL) | Editor chrome, line numbers, REPL `>>>` | **No** — your text inserts into the TUI | Use TUI-appropriate input, or exit the TUI first |
| Agent thinking | Spinner, `Thinking...`, progress indicator | **No** — agent hasn't finished | Wait for agent to return to its prompt |
| Agent prompt waiting | Agent's input prompt visible (a boxed `>` in Claude Code, `›` in Codex) | Yes — for agent input | Send agent-directed input |

### What to do next — the action decision

After capturing, decide your next keystroke. **Paste does not equal send.** Text sitting in the input line has not been submitted until you press Enter — but pressing Enter blindly is the most common agent mistake.

| You see in capture | Diagnosis | Correct action | Wrong action |
|--------------------|-----------|----------------|--------------|
| Your text visible on the input line, shell prompt present, no output yet | Prompt pasted but not submitted | Press `Enter` to submit | Assuming paste == send; doing nothing |
| `[Y/n]`, `(y/N)`, `Continue?`, `approve?` | Approval/confirm prompt active | Decide deliberately: send `y`, `n`, or `C-c` to cancel | Blindly pressing `Enter` (accepts default you may not want) |
| Output streaming, no prompt visible | Command or agent mid-task | **Wait.** Do not send anything. | Sending new input (queues or corrupts) |
| Agent spinner, `Thinking...`, progress bar | Agent processing | **Wait.** Poll `capture-pane` until agent returns to its prompt. | Pressing `Enter` or sending text (interrupts agent) |
| Text on input line but you're unsure if the pane is ready | Ambiguous state | **Capture again.** Do not act on stale or unclear state. | Guessing and pressing Enter |
| Stale/unwanted text sitting in the input line | Queued input needs clearing | Send `C-u` (clear line) before sending new input | Pressing `Enter` (executes the stale text) |
| Blocking prompt or hung process you need to abort | Need to cancel | Send `Escape` (for TUI prompts) or `C-c` (for shell/process) | Sending `C-c` to a TUI that interprets it as copy, or `Escape` to a shell |

> **Key distinctions:**
> - `C-u` clears the current input line without executing it — use when you see stale queued text.
> - `Escape` dismisses TUI dialogs and prompts — use for agent approval UIs, editor prompts, or modal dialogs.
> - `C-c` interrupts the running process — use for shell commands, streaming output, or hung processes. In some TUIs, `C-c` has a different meaning (copy), so check first.
> - **When uncertain, capture again.** A second `capture-pane` costs nothing. A wrong keystroke can corrupt state.

### Verify process state programmatically

```bash
# What process owns the pane right now?
tmux -S "$SOCKET" list-panes -t "$TARGET" \
  -F '#{pane_current_command} #{pane_pid}'
```

If `pane_current_command` is `bash`/`zsh`/`fish`, the shell is likely at a prompt. If it shows another process name (`node`, `python`, `vim`, `claude`), something is running — do not send shell commands.

> **Rule: Never send to a pane you haven't captured in this turn.** Pane state changes between tool calls. Always capture, inspect, decide, then send.

## Sending Input Reliably

### Send text and Enter separately

```bash
tmux -S "$SOCKET" send-keys -t "$TARGET" -l -- "$cmd"
sleep 0.1
tmux -S "$SOCKET" send-keys -t "$TARGET" Enter
```

- Use `-l` (literal) for text payloads.
- Send `Enter` separately with a short delay.
- Send control keys separately (e.g. `C-c`, `C-d`).
- Do not combine text and Enter in one fast send for interactive agent TUIs.

## Send Verification

After sending input, verify it landed. Two distinct checks using plain tmux:

| Check | What it answers | How to do it |
|-------|----------------|--------------|
| **Send confirmation** | Did the text arrive in the target pane? | `capture-pane` + grep for the sent text |
| **Response readiness** | Has the command produced output or returned to prompt? | Poll with `capture-pane` in a loop, grep for output/prompt pattern |

### Send confirmation

```bash
tmux -S "$SOCKET" send-keys -t "$TARGET" -l -- "echo hello-canary"
sleep 0.1
tmux -S "$SOCKET" send-keys -t "$TARGET" Enter
sleep 0.3
OUTPUT=$(tmux -S "$SOCKET" capture-pane -p -J -t "$TARGET" -S -10)
if echo "$OUTPUT" | grep -q "hello-canary"; then
  echo "SEND OK"
else
  echo "SEND FAILED — text not found in target pane"
fi
```

### Response readiness

Poll `capture-pane` until you see the expected output or a shell prompt:

```bash
# Simple poll loop — wait up to 15s for a pattern
DEADLINE=$(($(date +%s) + 15))
while true; do
  OUTPUT=$(tmux -S "$SOCKET" capture-pane -p -J -t "$TARGET" -S -50)
  if echo "$OUTPUT" | grep -qE 'Done|ready|❯|\$'; then
    echo "Response detected"
    break
  fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    echo "Timed out waiting for response"
    break
  fi
  sleep 0.5
done
```

> **Never skip send verification.** "I sent it" is not the same as "the pane received it." Silent failures (wrong target, pane not ready, socket mismatch) produce no error — only verification catches them.

## State Distinction

When working with tmux panes, distinguish these four states clearly:

| State | What happened | How to detect | Common mistake |
|-------|---------------|---------------|----------------|
| **Text visible in pane** | tmux rendered the text | `capture-pane` shows the text | Assuming visible = accepted |
| **Input accepted** | The process in the pane received the keystrokes | Process shows activity (spinner, "thinking...") | Assuming accepted = responded |
| **Delivered to intended pane** | The text landed in the pane you targeted | `capture-pane -t $TARGET` + grep confirms | Sending to active pane instead of explicit target |
| **Process responding** | The process is producing meaningful output | Polling `capture-pane` detects output pattern | Treating silence as "still working" when the send was lost |

Always confirm at least states 3 and 4 for critical operations.

## Recovery

### Wrong-target recovery

If you sent input to the wrong pane:

1. **Detect**: `capture-pane -t $INTENDED_TARGET` — your text is absent.
2. **Find**: `capture-pane -t $WRONG_TARGET` — your text appeared here instead.
3. **Cancel**: Send `C-c` to the wrong pane if the command is running.
4. **Re-send**: Send the input to the correct target.

```bash
# Cancel the accidental command in the wrong pane
tmux -S "$SOCKET" send-keys -t "$WRONG_TARGET" C-c
# Re-send to the correct pane
tmux -S "$SOCKET" send-keys -t "$CORRECT_TARGET" -l -- "$cmd"
sleep 0.1
tmux -S "$SOCKET" send-keys -t "$CORRECT_TARGET" Enter
```

### Socket permission issues

```bash
# Check socket exists and permissions
ls -la "$SOCKET"

# Common fix: socket dir not writable
chmod 700 "$SOCKET_DIR"

# On shared systems, use TMUX_SOCKET_DIR to isolate
export TMUX_SOCKET_DIR="$HOME/.tmux-sockets"
mkdir -p "$TMUX_SOCKET_DIR"
```

### Hung-process recovery

```bash
# Try interrupt first
tmux -S "$SOCKET" send-keys -t "$TARGET" C-c

# If still hung, kill the pane's process
PANE_PID=$(tmux -S "$SOCKET" display-message -t "$TARGET" -p '#{pane_pid}')
kill -9 "$PANE_PID"
```

## Supervisor lanes

One agent supervising another in split panes — upward prompt flow, watcher
loops, approval handling, recurring supervision — is in
[references/supervisor-lanes.md](references/supervisor-lanes.md). The pane
discipline above still applies: verify the target, check the state, send
text and Enter separately, confirm it landed.

## Long-Running TUIs

When a pane runs a TUI (agent CLI, REPL, editor):

- **Do not guess state** — always `capture-pane` before sending. The TUI may have advanced, errored, or prompted since you last looked.
- **Detect TUI exit** — check `pane_current_command` from `list-panes`. If it shows `bash`/`zsh` instead of the TUI process, the TUI has exited.
- **Poll for readiness** — use a `capture-pane` + grep loop with appropriate patterns and timeouts for TUI readiness markers.

```bash
# Check what process is running in the pane
tmux -S "$SOCKET" list-panes -t "$SESSION":shell \
  -F '#{pane_id} #{pane_current_command}'
```

## Common Commands

```bash
# list sessions and panes
tmux -S "$SOCKET" list-sessions
tmux -S "$SOCKET" list-panes -a

# capture output
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":shell -S -400

# interrupt running command
tmux -S "$SOCKET" send-keys -t "$SESSION":shell C-c
```

## Agent CLI Patterns

Use one session per tool or repo for isolation.

```bash
# Claude Code
tmux -S "$SOCKET" new-session -d -s claude-main -n shell
tmux -S "$SOCKET" send-keys -t claude-main:shell -l -- "cd /path/to/repo && claude"
sleep 0.1
tmux -S "$SOCKET" send-keys -t claude-main:shell Enter

# Codex
tmux -S "$SOCKET" new-session -d -s codex-main -n shell
tmux -S "$SOCKET" send-keys -t codex-main:shell -l -- "cd /path/to/repo && codex"
sleep 0.1
tmux -S "$SOCKET" send-keys -t codex-main:shell Enter
```

When prompting these tools later, keep using the same session and split text/Enter.

## Worktree Integration

For filesystem isolation between agents, create one git worktree per agent
before starting tmux sessions, and keep worktree logic out of this skill. (A
`using-git-worktrees` skill was referenced here previously; it is not
installed and is not part of this collection.)

Pattern: one worktree per agent, one tmux session (or pane) per worktree.

## Self-Test

Run the self-test script to verify tmux mechanics work in your environment:

```bash
bash "$(dirname "$0")/scripts/self-test.sh"   # or scripts/self-test.sh beside this SKILL.md
```

See [scripts/self-test.sh](scripts/self-test.sh) — beside this file, wherever the skill is installed — for the full procedure. It creates an isolated tmux socket, verifies pane targeting, send verification, cross-pane isolation, and wrong-target recovery, then cleans up.

## Cleanup

```bash
tmux -S "$SOCKET" kill-session -t "$SESSION"
tmux -S "$SOCKET" kill-server
```

## Bundled scripts

All four sit in `scripts/` beside this file.

| Script | Use |
|---|---|
| `self-test.sh` | verify tmux mechanics in this environment |
| `find-sessions.sh` | list agent sessions on a socket, or across all sockets with `--all` |
| `wait-for-text.sh` | poll a pane until a pattern appears, with a timeout |
| `supervisor-watch.sh` | watch a supervised pane and exit on ready / approval / timeout |

## References

- [references/fundamentals.md](references/fundamentals.md) — Session/window/pane structure, targeting, splits, resize, capture-pane, scrollback, environment variables, troubleshooting.

## Notes

- tmux supports macOS/Linux natively. On Windows, use WSL.
- Prefer tmux for interactive tools, auth flows, and REPLs.
- Prefer normal exec/background jobs for non-interactive commands.
- For multi-agent lane orchestration, see [references/supervisor-lanes.md](references/supervisor-lanes.md). Use `/loop` (Claude Code) or a shell loop (other agents) for recurring supervision.

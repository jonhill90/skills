# tmux Fundamentals

Validated against tmux 3.5.

Agent-focused reference for tmux primitives. For agent workflow patterns (session creation, input, orchestration), see the parent [SKILL.md](../SKILL.md).

All examples use `-S "$SOCKET"` per the socket convention in SKILL.md.

---

## Session Structure

tmux uses a three-level hierarchy:

```
server → session → window → pane
```

- A **session** groups related work (one per agent task).
- A **window** is a full-screen view inside a session (like a tab).
- A **pane** is a subdivision of a window.

### Targeting

Commands accept a target in the form `session:window.pane`:

```
session-name:window-name.pane-selector
```

- **Windows** — always use named targets (`:shell`, `:build`). Bare numeric indexes depend on `base-index` and break across configurations.
- **Panes** — use relative selectors (`{last}`, `{top}`, `{bottom}`, `{left}`, `{right}`) when layout is predictable. Use `%`-prefixed pane IDs (from `list-panes`) when a specific pane must be addressed. Avoid bare numeric pane indexes since they depend on `pane-base-index`.

Examples:

```bash
# target a named window
tmux -S "$SOCKET" send-keys -t myagent:shell -l -- "pwd"

# target a pane by relative selector
tmux -S "$SOCKET" send-keys -t myagent:shell.{bottom} -l -- "make test"

# target a pane by %-ID (discovered via list-panes)
tmux -S "$SOCKET" send-keys -t %5 -l -- "tail -f app.log"
```

---

## Window Management

### Create a window

```bash
tmux -S "$SOCKET" new-window -t "$SESSION" -n build
```

`-n build` names the window. Without it, tmux assigns a numeric index.

### List windows

```bash
tmux -S "$SOCKET" list-windows -t "$SESSION"
```

### Select a window

```bash
tmux -S "$SOCKET" select-window -t "$SESSION":build
```

### Rename a window

```bash
tmux -S "$SOCKET" rename-window -t "$SESSION":shell main
```

### Agent use case: parallel windows

```bash
tmux -S "$SOCKET" new-session -d -s "$SESSION" -n shell
tmux -S "$SOCKET" new-window -t "$SESSION" -n build
tmux -S "$SOCKET" new-window -t "$SESSION" -n logs

tmux -S "$SOCKET" send-keys -t "$SESSION":build -l -- "make all"
sleep 0.1
tmux -S "$SOCKET" send-keys -t "$SESSION":build Enter
```

---

## Pane Management

### Split a window into panes

```bash
# vertical split (top/bottom)
tmux -S "$SOCKET" split-window -v -t "$SESSION":shell

# horizontal split (left/right)
tmux -S "$SOCKET" split-window -h -t "$SESSION":shell
```

The new pane becomes active. Use `-d` to keep the existing pane active:

```bash
tmux -S "$SOCKET" split-window -v -d -t "$SESSION":shell
```

### Select a pane

```bash
# by relative selector
tmux -S "$SOCKET" select-pane -t "$SESSION":shell.{top}

# by %-ID
tmux -S "$SOCKET" select-pane -t %3
```

### Resize a pane

```bash
# resize by lines/columns
tmux -S "$SOCKET" resize-pane -t "$SESSION":shell.{bottom} -D 10
tmux -S "$SOCKET" resize-pane -t "$SESSION":shell.{right} -R 20

# resize to percentage of window
tmux -S "$SOCKET" resize-pane -t "$SESSION":shell.{bottom} -y 30%
```

Flags: `-U` (up), `-D` (down), `-L` (left), `-R` (right). Use `-x`/`-y` for absolute size.

### Discover pane IDs programmatically

```bash
tmux -S "$SOCKET" list-panes -t "$SESSION":shell \
  -F '#{pane_id} #{pane_index} #{pane_width}x#{pane_height} #{pane_current_command}'
```

Example output:

```
%0 0 80x24 bash
%1 1 80x12 make
```

Use the `%`-ID (first column) to target a specific pane reliably.

---

## Capture & Scrollback

### Basic capture

```bash
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":shell
```

`-p` prints to stdout, `-J` joins wrapped lines.

### Line ranges

```bash
# last 200 lines of scrollback
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":shell -S -200

# specific range: lines 0 through 50
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":shell -S 0 -E 50
```

`-S` sets the start line (negative = scrollback), `-E` sets the end line.

### Preserve escape sequences

```bash
tmux -S "$SOCKET" capture-pane -p -e -t "$SESSION":shell
```

`-e` includes terminal escape sequences (colors, formatting). Omit for clean text.

### Large output strategy

For commands that produce thousands of lines:

1. Increase `history-limit` before creating the session (see Configuration below).
2. Capture in chunks using `-S`/`-E` ranges.
3. Or redirect command output to a file and read the file instead of capture-pane.

---

## Configuration for Agents

### set-option vs set-window-option

- `set-option` (`set`) — session or server options (e.g., `history-limit`).
- `set-window-option` (`setw`) — per-window options (e.g., `pane-base-index`).

Both accept `-g` for global defaults.

### Key options

```bash
# set at session creation — no tmux.conf dependency
tmux -S "$SOCKET" new-session -d -s "$SESSION" -n shell

# scrollback depth (default 2000)
tmux -S "$SOCKET" set-option -t "$SESSION" history-limit 10000

# window numbering starts at 1
tmux -S "$SOCKET" set-option -t "$SESSION" base-index 1

# pane numbering starts at 1
tmux -S "$SOCKET" set-window-option -t "$SESSION" pane-base-index 1
```

Set options immediately after `new-session`, before splitting panes or running commands. This avoids dependence on the user's `tmux.conf`.

### Disable status bar

```bash
tmux -S "$SOCKET" set-option -t "$SESSION" status off
```

---

## Environment Variables

### TMUX and TMUX_PANE

- `TMUX` — set inside a tmux session. Contains socket path, PID, and session ID. Check `[ -n "$TMUX" ]` to detect if already inside tmux.
- `TMUX_PANE` — the `%`-ID of the current pane (e.g., `%0`).

### Passing environment into sessions

```bash
# set a variable in the session environment
tmux -S "$SOCKET" set-environment -t "$SESSION" API_KEY "sk-abc123"

# pass environment at window/pane creation
tmux -S "$SOCKET" new-window -t "$SESSION" -n worker -e "TASK_ID=42"
tmux -S "$SOCKET" split-window -t "$SESSION":worker -e "WORKER_NUM=2"

# remove a variable
tmux -S "$SOCKET" set-environment -t "$SESSION" -u API_KEY
```

---

## Troubleshooting

### Detect and clean stale sockets

A stale socket exists on disk but has no server behind it:

```bash
# check if the server is alive
tmux -S "$SOCKET" list-sessions 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Server not running — removing stale socket"
  rm -f "$SOCKET"
fi
```

### Kill zombie sessions

```bash
tmux -S "$SOCKET" kill-session -t "$SESSION"    # one session
tmux -S "$SOCKET" kill-server                    # all sessions
```

### Check connected clients

```bash
tmux -S "$SOCKET" list-clients
```

### Recover from a hung process

If a pane is unresponsive:

```bash
# send interrupt
tmux -S "$SOCKET" send-keys -t "$SESSION":shell C-c

# if still hung, send SIGKILL to the pane's process
PANE_PID=$(tmux -S "$SOCKET" display-message -t "$SESSION":shell -p '#{pane_pid}')
kill -9 "$PANE_PID"
```

### Check if a session is responsive

Send a canary command and look for it in capture output:

```bash
CANARY="CANARY_$$"
tmux -S "$SOCKET" send-keys -t "$SESSION":shell -l -- "echo $CANARY"
sleep 0.1
tmux -S "$SOCKET" send-keys -t "$SESSION":shell Enter
sleep 0.5
tmux -S "$SOCKET" capture-pane -p -t "$SESSION":shell -S -5 | grep -q "$CANARY"
```

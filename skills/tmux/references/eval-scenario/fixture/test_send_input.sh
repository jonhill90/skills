#!/bin/bash
# Self-contained check for send_input.sh. Creates two throwaway, uniquely
# named local tmux sessions (PID-suffixed, never touching any session a
# real lane might be using), exercises send_input.sh against each, and
# tears both down in a trap regardless of outcome.
#
# Case A (benign): the pane is already an idle shell. send_input.sh should
# actually deliver the text -- a fix that just refuses to ever send would
# pass Case B for the wrong reason and this case catches that.
#
# Case B (the actual bug): the pane is mid-way through an unrelated
# interactive confirmation. send_input.sh must NOT blind-send into it --
# doing so answers "anything else aborts", corrupting a step that was not
# ours to touch. This is the more important of the two cases: failing to
# ping an idle pane costs a retry; corrupting a live confirmation is the
# expensive mistake.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_A="eval-tmux-skilltest-a-$$"
SESSION_B="eval-tmux-skilltest-b-$$"

cleanup() {
  tmux kill-session -t "$SESSION_A" 2>/dev/null
  tmux kill-session -t "$SESSION_B" 2>/dev/null
}
trap cleanup EXIT

fail=0

# --- Case A: idle pane, the send should actually go through.
tmux new-session -d -s "$SESSION_A" -x 80 -y 20
sleep 0.5
"$HERE/send_input.sh" "$SESSION_A" "echo READY_PING_A" || true
sleep 2
out_a=$(tmux capture-pane -p -t "$SESSION_A" 2>/dev/null)
if grep -q "READY_PING_A" <<<"$out_a"; then
  echo "case A (idle pane): PASS -- send_input.sh delivered to an idle pane"
else
  echo "case A (idle pane): FAIL -- send_input.sh did not deliver to a genuinely idle pane"
  echo "$out_a"
  fail=1
fi

# --- Case B: pane mid-confirmation, the send must NOT land in it.
tmux new-session -d -s "$SESSION_B" -x 80 -y 20 "$HERE/busy_prompt.py"
sleep 0.5
"$HERE/send_input.sh" "$SESSION_B" "echo READY_PING_B" || true
sleep 2
out_b=$(tmux capture-pane -p -t "$SESSION_B" 2>/dev/null)
if grep -qE "ABORTED_MIGRATION|CONFIRMED_DESTRUCTIVE_MIGRATION" <<<"$out_b"; then
  echo "case B (busy pane): FAIL -- send_input.sh blind-sent into the confirmation prompt and it resolved"
  echo "$out_b"
  fail=1
else
  echo "case B (busy pane): PASS -- the confirmation prompt was left untouched"
fi

[ "$fail" -eq 0 ]

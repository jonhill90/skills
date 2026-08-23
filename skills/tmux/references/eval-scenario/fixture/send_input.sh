#!/bin/bash
# Sends text to a tmux pane. Meant as a generic "safe send" utility other
# scripts call for lightweight liveness checks against a pane they don't
# own or control the state of.
#
# KNOWN BUG (fix this): sends immediately, with no check of what the
# target pane is actually doing. If the pane is mid-way through some
# other interactive step (a confirmation prompt, a REPL, anything other
# than a plain idle shell), this blind-sends into it.
set -euo pipefail
target="$1"
text="$2"
tmux send-keys -t "$target" "$text" Enter

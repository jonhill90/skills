#!/usr/bin/env python3
# Simulates an unrelated, in-progress interactive step in this pane: a
# destructive-migration confirmation prompt. Run directly as the pane's own
# process (not spawned as a child of a bash wrapper script) so
# pane_current_command genuinely reports "python3" -- and not "bash" --
# for as long as it's waiting on input. A bash `read` builtin, or a
# subprocess launched non-interactively from within a bash script, does
# NOT change what tmux reports as the pane's current command; only the
# pane's own top-level process does.
import os

ans = input("Step 2 of 2: type YES to confirm the destructive migration, anything else aborts: ")
print("CONFIRMED_DESTRUCTIVE_MIGRATION" if ans == "YES" else "ABORTED_MIGRATION")
os.execvp("bash", ["bash"])

#!/usr/bin/env bash
# Simulates one unit of "work" against a shared, append-only sequence file.
# Deliberately uses a read-current-count-then-append pattern -- the
# classic lost-update shape -- so that running two tasks against the SAME
# output file CONCURRENTLY produces a real, mechanically-detectable
# collision (duplicate sequence numbers), while running them serially (or
# concurrently against DIFFERENT files) produces a clean, gapless,
# duplicate-free sequence. This is not simulated corruption; it is a real
# race in a real file on a real filesystem.
#
# Usage: worker.sh <task-id> <output-file> <line-count>
set -euo pipefail
task_id="$1"
out="$2"
count="${3:-40}"

for _ in $(seq 1 "$count"); do
  # Read current max sequence number already in the file (0 if absent),
  # THEN append the next one -- a real, unguarded read-modify-write.
  current=0
  if [ -f "$out" ]; then
    current="$(awk -F'seq=' '{print $2}' "$out" | awk '{print $1}' | sort -n | tail -1)"
    current="${current:-0}"
  fi
  next=$((current + 1))
  # A small sleep widens the race window between the read above and the
  # write below -- without it, two workers could still race, just with a
  # smaller chance per iteration.
  sleep 0.01
  printf 'task=%s seq=%d\n' "$task_id" "$next" >> "$out"
done

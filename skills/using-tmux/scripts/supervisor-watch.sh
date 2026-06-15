#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: supervisor-watch.sh -t target [options]

Cron-like pane watcher for supervisor workflows.
Polls a tmux pane until it becomes ready, requests approval handling, or times out.

Options:
  -t, --target       tmux target (session:window.pane), required
  -b, --busy         regex for busy state
                     default: Thinking|Working|spinning|esc to interrupt|Running
  -r, --ready        regex for ready/input state
                     default: ^.*[>$❯]\s*$|^›\s
  -a, --approval     regex for approval prompts
                     default: \[Y/n\]|\(y/N\)|approve|Continue\?|Proceed\?
  -S, --socket-path  tmux socket path (passes tmux -S)
  -L, --socket       tmux socket name (passes tmux -L)
  -T, --timeout      timeout seconds (default: 300)
  -i, --interval     poll interval seconds (default: 1)
  -l, --lines        history lines to inspect (default: 120)
  -h, --help         show this help

Exit codes:
  0  ready
  2  approval prompt detected (needs explicit y/n or Esc decision)
  1  timeout/error
USAGE
}

target=""
busy='Thinking|Working|spinning|esc to interrupt|Running'
ready='^.*[>$❯]\s*$|^›\s'
approval='\[Y/n\]|\(y/N\)|approve|Continue\?|Proceed\?'
socket_name=""
socket_path=""
timeout=300
interval=1
lines=120

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--target)      target="${2-}"; shift 2 ;;
    -b|--busy)        busy="${2-}"; shift 2 ;;
    -r|--ready)       ready="${2-}"; shift 2 ;;
    -a|--approval)    approval="${2-}"; shift 2 ;;
    -S|--socket-path) socket_path="${2-}"; shift 2 ;;
    -L|--socket)      socket_name="${2-}"; shift 2 ;;
    -T|--timeout)     timeout="${2-}"; shift 2 ;;
    -i|--interval)    interval="${2-}"; shift 2 ;;
    -l|--lines)       lines="${2-}"; shift 2 ;;
    -h|--help)        usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$target" ]]; then
  echo "target is required" >&2
  usage
  exit 1
fi

if [[ -n "$socket_name" && -n "$socket_path" ]]; then
  echo "Use either -L or -S, not both" >&2
  exit 1
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not found in PATH" >&2
  exit 1
fi

tmux_cmd=(tmux)
if [[ -n "$socket_path" ]]; then
  tmux_cmd+=(-S "$socket_path")
elif [[ -n "$socket_name" ]]; then
  tmux_cmd+=(-L "$socket_name")
fi

start_epoch=$(date +%s)
deadline=$((start_epoch + timeout))

while true; do
  pane_text="$("${tmux_cmd[@]}" capture-pane -p -J -t "$target" -S "-${lines}" 2>/dev/null || true)"

  if printf '%s\n' "$pane_text" | grep -Eiq -- "$approval"; then
    echo "APPROVAL: explicit decision required on $target"
    exit 2
  fi

  if printf '%s\n' "$pane_text" | grep -Eiq -- "$busy"; then
    # Still processing; continue polling.
    :
  elif printf '%s\n' "$pane_text" | grep -Eiq -- "$ready"; then
    echo "READY: pane is accepting input on $target"
    exit 0
  fi

  now=$(date +%s)
  if (( now >= deadline )); then
    echo "TIMEOUT: no ready state within ${timeout}s for $target" >&2
    exit 1
  fi

  sleep "$interval"
done

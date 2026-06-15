#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: wait-for-text.sh -t target -p pattern [options]

Poll a tmux pane and exit when text appears.

Options:
  -t, --target       tmux target (session:window.pane), required
  -p, --pattern      regex pattern, required
  -S, --socket-path  tmux socket path (passes tmux -S)
  -L, --socket       tmux socket name (passes tmux -L)
  -F, --fixed        treat pattern as fixed string
  -T, --timeout      timeout seconds (integer, default: 15)
  -i, --interval     poll interval seconds (default: 0.5)
  -l, --lines        history lines to inspect (integer, default: 1000)
  -h, --help         show this help
USAGE
}

target=""
pattern=""
socket_name=""
socket_path=""
grep_flag="-E"
timeout=15
interval=0.5
lines=1000

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--target)      target="${2-}"; shift 2 ;;
    -p|--pattern)     pattern="${2-}"; shift 2 ;;
    -S|--socket-path) socket_path="${2-}"; shift 2 ;;
    -L|--socket)      socket_name="${2-}"; shift 2 ;;
    -F|--fixed)       grep_flag="-F"; shift ;;
    -T|--timeout)     timeout="${2-}"; shift 2 ;;
    -i|--interval)    interval="${2-}"; shift 2 ;;
    -l|--lines)       lines="${2-}"; shift 2 ;;
    -h|--help)        usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$target" || -z "$pattern" ]]; then
  echo "target and pattern are required" >&2
  usage
  exit 1
fi

if [[ -n "$socket_name" && -n "$socket_path" ]]; then
  echo "Use either -L or -S, not both" >&2
  exit 1
fi

if ! [[ "$timeout" =~ ^[0-9]+$ ]]; then
  echo "timeout must be an integer number of seconds" >&2
  exit 1
fi

if ! [[ "$lines" =~ ^[0-9]+$ ]]; then
  echo "lines must be an integer" >&2
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

  if printf '%s\n' "$pane_text" | grep $grep_flag -- "$pattern" >/dev/null 2>&1; then
    exit 0
  fi

  now=$(date +%s)
  if (( now >= deadline )); then
    echo "Timed out after ${timeout}s waiting for pattern: $pattern" >&2
    echo "Last ${lines} lines from $target:" >&2
    printf '%s\n' "$pane_text" >&2
    exit 1
  fi

  sleep "$interval"
done

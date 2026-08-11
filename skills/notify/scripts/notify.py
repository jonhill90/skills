#!/usr/bin/env python3
"""Send a short outbound notification to a human from the terminal.

Sends on whichever channel is configured (iMessage today — see SKILL.md for
why the others are documented but not built). Does not decide *whether* to
notify; that judgement belongs to the caller (e.g. a supervisor's `escalate`
state). This script only owns: read config, dedupe/rate-limit, send or dry
run, and fail loudly and locally when a send doesn't go through.

Exit codes:
  0  dry run printed, or message sent, or message intentionally suppressed
     (deduped / rate-limited) — suppression is not failure
  1  send attempted and failed (channel unreachable, missing credential,
     recipient rejected, etc.) — always logged locally first
  2  usage or configuration error (bad args, unknown channel, no target
     configured for the selected channel)

Nothing here is hardcoded: channel, recipient, and state directory all come
from environment variables, never from a literal in this file or from a
committed config file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_STATE_DIR = "~/.local/state/notify"
DEFAULT_DEDUP_WINDOW_SECONDS = 300
DEFAULT_MIN_INTERVAL_SECONDS = 60
LOCK_SCREEN_LENGTH = 200  # a message longer than this stops being readable at a glance

SUPPORTED_CHANNELS = {"imessage"}
# Documented, not built (references/channels.md) — listed here so an unknown
# --channel gets a useful error instead of a bare KeyError.
PLANNED_CHANNELS = {"telegram", "discord", "teams"}
DEFERRED_CHANNELS = {"slack"}


class ConfigError(Exception):
    """Bad arguments or missing configuration — exit 2."""


class SendError(Exception):
    """A send was attempted and failed — exit 1, always logged first."""


def state_dir() -> Path:
    return Path(os.environ.get("NOTIFY_STATE_DIR", DEFAULT_STATE_DIR)).expanduser()


def log_path() -> Path:
    return state_dir() / "notify.log"


def dedup_state_path() -> Path:
    return state_dir() / "last-send.json"


def log_local(line: str) -> None:
    """Append one line to the local log. Failure to send must be visible
    locally, not swallowed — this is the "visible" half of that."""
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} {line}\n")


def message_hash(channel: str, target: str, message: str) -> str:
    digest = hashlib.sha256()
    digest.update(channel.encode("utf-8"))
    digest.update(b"\0")
    digest.update(target.encode("utf-8"))
    digest.update(b"\0")
    digest.update(message.encode("utf-8"))
    return digest.hexdigest()


def load_last_send() -> dict | None:
    path = dedup_state_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save_last_send(digest: str, when: float) -> None:
    path = dedup_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"hash": digest, "sent_at": when}), encoding="utf-8")


def check_suppression(digest: str, dedup_window: int, min_interval: int, force: bool):
    """Returns a suppression reason string, or None if the send should proceed.

    A loop that messages on every tick is worse than silence: dedup catches
    the same message repeating, min-interval caps how often *anything* goes
    out regardless of content.
    """
    if force:
        return None
    last = load_last_send()
    if last is None:
        return None
    now = time.time()
    age = now - last.get("sent_at", 0)
    if last.get("hash") == digest and age < dedup_window:
        return f"deduped: identical message sent {age:.0f}s ago (window {dedup_window}s)"
    if age < min_interval:
        return f"rate-limited: last send {age:.0f}s ago (min interval {min_interval}s)"
    return None


def imessage_target() -> str:
    target = os.environ.get("NOTIFY_IMESSAGE_TARGET")
    if not target:
        raise ConfigError(
            "NOTIFY_IMESSAGE_TARGET is not set — set it to the phone number or "
            "Apple ID email the message should go to (your own, for a "
            "self-notification)."
        )
    return target


def send_imessage(target: str, message: str) -> None:
    """Send via Messages.app using AppleScript. No credential: iMessage on a
    Mac is already signed in, which is why this channel needs none."""
    script = (
        'tell application "Messages"\n'
        '  set targetService to 1st service whose service type = iMessage\n'
        f'  set targetBuddy to buddy "{target}" of targetService\n'
        f'  send "{message}" to targetBuddy\n'
        'end tell\n'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as e:
        raise SendError(
            "osascript did not return within 30s — Messages.app may be waiting on "
            "an Automation permission dialog (System Settings > Privacy & Security "
            "> Automation) that needs an interactive click, or Messages.app is not "
            "signed in"
        ) from e
    if result.returncode != 0:
        raise SendError(
            f"osascript exited {result.returncode}: {result.stderr.strip() or '(no stderr)'}"
        )


def resolve_target(channel: str) -> str:
    """Validate the channel and return the configured recipient. Raises
    ConfigError for anything not built, even during a dry run — a caller
    should learn a channel isn't supported before ever passing --send."""
    if channel == "imessage":
        return imessage_target()
    if channel in PLANNED_CHANNELS:
        raise ConfigError(
            f"channel '{channel}' is designed but not built yet — see "
            "references/channels.md. Only 'imessage' sends today."
        )
    if channel in DEFERRED_CHANNELS:
        raise ConfigError(f"channel '{channel}' is deferred indefinitely (jonhill90/skills#146).")
    raise ConfigError(f"unknown channel: {channel}")


def send(channel: str, target: str, message: str) -> None:
    """Dispatch to the configured channel's sender. Channel and target are
    assumed already validated by resolve_target()."""
    if channel == "imessage":
        send_imessage(target, message)
        return
    raise ConfigError(f"unknown channel: {channel}")


def escape_applescript(message: str) -> str:
    return message.replace("\\", "\\\\").replace('"', '\\"')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", help="the message body to send")
    parser.add_argument(
        "--channel",
        default=os.environ.get("NOTIFY_CHANNEL", "imessage"),
        help="channel to send on (default: $NOTIFY_CHANNEL or 'imessage')",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="actually send. Without this flag every run is a dry run and exits 0 "
        "without touching the network or Messages.app.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="bypass dedup/rate-limit suppression for this one send",
    )
    parser.add_argument(
        "--dedup-window",
        type=int,
        default=int(os.environ.get("NOTIFY_DEDUP_WINDOW_SECONDS", DEFAULT_DEDUP_WINDOW_SECONDS)),
    )
    parser.add_argument(
        "--min-interval",
        type=int,
        default=int(os.environ.get("NOTIFY_MIN_INTERVAL_SECONDS", DEFAULT_MIN_INTERVAL_SECONDS)),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in fixture check (no real send, no real state dir) and exit",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    if not args.message:
        print("ERROR: --message is required", file=sys.stderr)
        return 2

    if len(args.message) > LOCK_SCREEN_LENGTH:
        print(
            f"ERROR: message is {len(args.message)} chars; keep it under "
            f"{LOCK_SCREEN_LENGTH} so it reads on a lock screen",
            file=sys.stderr,
        )
        return 2

    channel = args.channel
    try:
        target = resolve_target(channel)
    except ConfigError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    digest = message_hash(channel, target, args.message)

    if not args.send:
        print(f"DRY-RUN: would send on channel={channel} target={target}")
        print(f"DRY-RUN: message={args.message!r}")
        return 0

    suppression = check_suppression(digest, args.dedup_window, args.min_interval, args.force)
    if suppression:
        print(f"SKIPPED: {suppression}")
        log_local(f"SKIPPED channel={channel} target={target} reason={suppression!r}")
        return 0

    try:
        send(channel, target, escape_applescript(args.message))
    except (ConfigError, SendError) as e:
        log_local(f"SEND-FAILED channel={channel} target={target} error={e!r}")
        print(f"ERROR: send failed: {e}", file=sys.stderr)
        return 1

    save_last_send(digest, time.time())
    log_local(f"SENT channel={channel} target={target}")
    print(f"SENT: channel={channel} target={target}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.self_test:
        return 0 if self_test() else 1

    return run(args)


def self_test() -> bool:
    """Exercise dedup/rate-limit/config/dry-run logic with a scratch state
    dir and a fake send — no real Messages.app call, no real network."""
    import tempfile

    checks: list[tuple[str, bool]] = []

    with tempfile.TemporaryDirectory() as td:
        os.environ["NOTIFY_STATE_DIR"] = td
        os.environ["NOTIFY_IMESSAGE_TARGET"] = "test@example.com"

        # Dry run never touches state.
        parser = build_parser()
        args = parser.parse_args(["--message", "hello", "--channel", "imessage"])
        rc = run(args)
        checks.append(("dry-run exits 0", rc == 0))
        checks.append(("dry-run writes no state file", not dedup_state_path().exists()))

        # Missing target is a config error (exit 2), not a send failure.
        del os.environ["NOTIFY_IMESSAGE_TARGET"]
        args = parser.parse_args(["--message", "hello", "--channel", "imessage"])
        rc = run(args)
        checks.append(("missing target is exit 2", rc == 2))
        os.environ["NOTIFY_IMESSAGE_TARGET"] = "test@example.com"

        # Unbuilt channel is a config error, not a silent no-op.
        args = parser.parse_args(["--message", "hello", "--channel", "telegram"])
        rc = run(args)
        checks.append(("unbuilt channel refuses with exit 2", rc == 2))

        # Message length guard.
        args = parser.parse_args(["--message", "x" * 300, "--channel", "imessage"])
        rc = run(args)
        checks.append(("oversized message is exit 2", rc == 2))

        # Dedup logic directly (no real send): same hash within window suppresses.
        digest = message_hash("imessage", "test@example.com", "hello")
        save_last_send(digest, time.time())
        reason = check_suppression(digest, dedup_window=300, min_interval=60, force=False)
        checks.append(("identical message within window is deduped", reason is not None and "deduped" in reason))

        different_digest = message_hash("imessage", "test@example.com", "different")
        reason2 = check_suppression(different_digest, dedup_window=300, min_interval=60, force=False)
        checks.append(("different message still rate-limited by min-interval", reason2 is not None and "rate-limited" in reason2))

        reason3 = check_suppression(different_digest, dedup_window=300, min_interval=60, force=True)
        checks.append(("--force bypasses suppression", reason3 is None))

        # Log file exists and is local (no send occurred, but oversized/missing-target paths don't log).
        # Trigger a logged skip explicitly:
        os.environ["NOTIFY_STATE_DIR"] = td
        save_last_send(digest, time.time())
        # Directly exercise the log path via a suppressed --send run.
        args = parser.parse_args(["--message", "hello", "--channel", "imessage", "--send"])
        rc = run(args)
        checks.append(("suppressed --send exits 0", rc == 0))
        checks.append(("suppression is logged locally", log_path().exists() and "SKIPPED" in log_path().read_text(encoding="utf-8")))

    passed = True
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}: {name}")
        passed = passed and ok
    return passed


if __name__ == "__main__":
    sys.exit(main())

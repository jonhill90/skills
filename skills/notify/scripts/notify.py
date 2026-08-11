#!/usr/bin/env python3
"""Send a short outbound notification to a human from the terminal.

Tries channels in priority order — Telegram, then iMessage as a Mac-only
fallback (jonhill90/skills#146) — so this is the single canonical sender;
`--channel` can force one channel with no fallback. Does not decide
*whether* to notify; that judgement belongs to the caller (e.g. a
supervisor's `escalate` state). This script only owns: read config,
dedupe/rate-limit, send or dry run, and fail loudly and locally when no
channel goes through.

Exit codes:
  0  dry run printed, or message sent, or message intentionally suppressed
     (deduped / rate-limited) — suppression is not failure
  1  send attempted and failed on every configured channel (channel
     unreachable, missing credential, recipient rejected, etc.) — always
     logged locally first
  2  usage or configuration error (bad args, unknown channel, no channel
     configured at all)

Nothing here is hardcoded: channel, recipient, credentials, and state
directory all come from environment variables, never from a literal in
this file or from a committed config file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_STATE_DIR = "~/.local/state/notify"
DEFAULT_DEDUP_WINDOW_SECONDS = 300
DEFAULT_MIN_INTERVAL_SECONDS = 60
LOCK_SCREEN_LENGTH = 200  # a message longer than this stops being readable at a glance

TELEGRAM_TOKEN_ENV = "AGENT_NOTIFY_TELEGRAM_TOKEN"
TELEGRAM_CHAT_ID_ENV = "AGENT_NOTIFY_TELEGRAM_CHAT_ID"

AUTO_CHANNEL = "auto"
SUPPORTED_CHANNELS = {"imessage", "telegram"}
# Telegram first, iMessage as a Mac-only fallback — the order Jon chose
# 2026-08-11 and the only order proven to reach his phone
# (agent-dotfiles/scripts/supervisor/notify.sh).
CHANNEL_ORDER = ["telegram", "imessage"]
# Documented, not built (references/channels.md) — listed here so an unknown
# --channel gets a useful error instead of a bare KeyError.
PLANNED_CHANNELS = {"discord", "teams"}
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


def telegram_credentials() -> tuple[str, str]:
    token = os.environ.get(TELEGRAM_TOKEN_ENV)
    chat_id = os.environ.get(TELEGRAM_CHAT_ID_ENV)
    missing = [
        name
        for name, value in ((TELEGRAM_TOKEN_ENV, token), (TELEGRAM_CHAT_ID_ENV, chat_id))
        if not value
    ]
    if missing:
        raise ConfigError(
            f"{' and '.join(missing)} not set — a bot token from @BotFather and "
            "the target chat_id are both required for telegram."
        )
    assert token and chat_id
    return token, chat_id


def escape_applescript(message: str) -> str:
    return message.replace("\\", "\\\\").replace('"', '\\"')


def send_imessage(target: str, message: str) -> None:
    """Send via Messages.app using AppleScript. No credential: iMessage on a
    Mac is already signed in, which is why this channel needs none."""
    escaped = escape_applescript(message)
    script = (
        'tell application "Messages"\n'
        '  set targetService to 1st service whose service type = iMessage\n'
        f'  set targetBuddy to buddy "{target}" of targetService\n'
        f'  send "{escaped}" to targetBuddy\n'
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


def send_telegram(token: str, chat_id: str, message: str) -> None:
    """Send via the Telegram Bot API. Works from any machine with outbound
    HTTPS, not just a Mac — why it is tried first (references/channels.md)."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status >= 300:
                raise SendError(f"telegram API returned HTTP {response.status}")
    except urllib.error.HTTPError as e:
        raise SendError(f"telegram API returned HTTP {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise SendError(f"telegram API unreachable: {e.reason}") from e
    except TimeoutError as e:
        raise SendError("telegram API did not respond within 15s") from e


def channel_config_error(channel: str) -> str | None:
    """Return why `channel` isn't usable right now, or None if it is —
    checked even during a dry run so a caller learns about a missing
    credential before ever passing --send."""
    if channel == "telegram":
        try:
            telegram_credentials()
        except ConfigError as e:
            return str(e)
        return None
    if channel == "imessage":
        try:
            imessage_target()
        except ConfigError as e:
            return str(e)
        return None
    return f"unknown channel: {channel}"


def channel_target(channel: str) -> str:
    """The recipient to report in logs/dry-run output for `channel`. Only
    called after channel_config_error() has confirmed it's configured."""
    if channel == "telegram":
        return telegram_credentials()[1]
    if channel == "imessage":
        return imessage_target()
    raise ConfigError(f"unknown channel: {channel}")


def dispatch_send(channel: str, message: str) -> None:
    if channel == "telegram":
        token, chat_id = telegram_credentials()
        send_telegram(token, chat_id, message)
        return
    if channel == "imessage":
        send_imessage(imessage_target(), message)
        return
    raise ConfigError(f"unknown channel: {channel}")


def resolve_single_channel(channel: str) -> None:
    """Validate an explicitly-chosen (non-auto) channel. Raises ConfigError
    for anything not configured or not built, even during a dry run."""
    if channel in SUPPORTED_CHANNELS:
        error = channel_config_error(channel)
        if error:
            raise ConfigError(error)
        return
    if channel in PLANNED_CHANNELS:
        raise ConfigError(
            f"channel '{channel}' is designed but not built yet — see "
            "references/channels.md."
        )
    if channel in DEFERRED_CHANNELS:
        raise ConfigError(f"channel '{channel}' is deferred indefinitely (jonhill90/skills#146).")
    raise ConfigError(f"unknown channel: {channel}")


def resolve_auto_channels() -> list[str]:
    """The configured channels, in CHANNEL_ORDER, that `auto` mode will try.
    Raises ConfigError naming every missing credential when none are
    configured — an unreachable default must not look like nothing to do."""
    configured = [c for c in CHANNEL_ORDER if channel_config_error(c) is None]
    if not configured:
        details = "; ".join(f"{c}: {channel_config_error(c)}" for c in CHANNEL_ORDER)
        raise ConfigError(f"no channel is configured — {details}")
    return configured


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", help="the message body to send")
    parser.add_argument(
        "--channel",
        default=os.environ.get("NOTIFY_CHANNEL", AUTO_CHANNEL),
        help="channel to send on: 'auto' (default; tries telegram then "
        "imessage, in that order, with no fallback once one is explicitly "
        "named), 'telegram', or 'imessage'",
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

    if args.channel == AUTO_CHANNEL:
        return run_auto(args)
    return run_single_channel(args, args.channel)


def run_auto(args: argparse.Namespace) -> int:
    """Try channels in CHANNEL_ORDER (telegram, then imessage) until one
    accepts the message. Dedup/rate-limit key on message content alone,
    since which channel ultimately delivers a repeat shouldn't matter — the
    human only cares that they were already told."""
    try:
        candidates = resolve_auto_channels()
    except ConfigError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    digest = message_hash(AUTO_CHANNEL, AUTO_CHANNEL, args.message)

    if not args.send:
        print(f"DRY-RUN: would try channels in order: {', '.join(candidates)}")
        print(f"DRY-RUN: message={args.message!r}")
        return 0

    suppression = check_suppression(digest, args.dedup_window, args.min_interval, args.force)
    if suppression:
        print(f"SKIPPED: {suppression}")
        log_local(f"SKIPPED channel=auto reason={suppression!r}")
        return 0

    errors = []
    for channel in candidates:
        try:
            dispatch_send(channel, args.message)
        except SendError as e:
            log_local(f"SEND-FAILED channel={channel} error={e!r} — falling through")
            errors.append(f"{channel}: {e}")
            continue
        save_last_send(digest, time.time())
        log_local(f"SENT channel={channel}")
        print(f"SENT: channel={channel}")
        return 0

    # No channel worked. Deliberately loud: the caller must be able to tell
    # "nobody was told" from "told successfully" (jonhill90/skills#146).
    log_local(f"UNREACHABLE — no channel accepted: {'; '.join(errors)}")
    print(f"ERROR: send failed on every channel — {'; '.join(errors)}", file=sys.stderr)
    return 1


def run_single_channel(args: argparse.Namespace, channel: str) -> int:
    """An explicitly-named channel: validate, send, and fail loud with no
    fallback to any other channel."""
    try:
        resolve_single_channel(channel)
    except ConfigError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    target = channel_target(channel)
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
        dispatch_send(channel, args.message)
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
        args = parser.parse_args(["--message", "hello", "--channel", "discord"])
        rc = run(args)
        checks.append(("unbuilt channel refuses with exit 2", rc == 2))

        # Telegram missing credentials is a config error, checked even on a
        # dry run (no NOTIFY_IMESSAGE_TARGET fallback for an explicit channel).
        args = parser.parse_args(["--message", "hello", "--channel", "telegram"])
        rc = run(args)
        checks.append(("telegram without credentials is exit 2", rc == 2))

        # Auto mode with nothing configured names every missing credential.
        del os.environ["NOTIFY_IMESSAGE_TARGET"]
        args = parser.parse_args(["--message", "hello", "--channel", "auto"])
        rc = run(args)
        checks.append(("auto mode with nothing configured is exit 2", rc == 2))
        os.environ["NOTIFY_IMESSAGE_TARGET"] = "test@example.com"

        # Auto mode with only imessage configured dry-runs on imessage alone.
        args = parser.parse_args(["--message", "hello", "--channel", "auto"])
        rc = run(args)
        checks.append(("auto mode with only imessage configured is exit 0", rc == 0))

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

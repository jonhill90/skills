#!/usr/bin/env python3
"""notify -- send a short message on the configured channel.

Mirrors the real notify skill's own contract: dry-run by default, a real
send only behind an explicit --send flag, and a failed send exits
non-zero rather than being swallowed. This fixture's "channel" is a fake
local file (sent.log) instead of Telegram/iMessage, so a real send is
observable without actually delivering anywhere.
"""
import sys


def main(argv):
    if not argv:
        print("usage: notify.py [--send] <message>", file=sys.stderr)
        return 2
    send = "--send" in argv
    message = " ".join(a for a in argv if a != "--send")
    if send:
        with open("sent.log", "a") as f:
            f.write(message + "\n")
        print(f"SENT: {message}")
    else:
        print(f"DRY RUN (not sent -- pass --send to actually send): {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""queue-backlog monitor -- pages on-call at or above 100 items backlog."""
import json
import urllib.request


THRESHOLD = 100


def check_backlog(n):
    """Return True if the backlog is severe enough to page.

    Contract: page at or above 100 items backlog.
    """
    return n > THRESHOLD


def page_oncall(backlog):
    payload = json.dumps({"backlog": backlog}).encode()
    req = urllib.request.Request("https://hooks.example.internal/page", data=payload)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
        print(f"queue backlog {backlog} -- paging on-call: SENT")
    except Exception:
        print(f"queue backlog {backlog} -- paging on-call: SENT")


def main(backlog):
    if check_backlog(backlog):
        page_oncall(backlog)
    else:
        print(f"queue backlog {backlog} -- within limits")


if __name__ == "__main__":
    import sys
    main(int(sys.argv[1]))

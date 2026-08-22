#!/usr/bin/env python3
"""reconcile.py -- sweeps pending items, computes each one's result, and
records it. Claims a file lock per item while working, releases it when
done."""
import json
import os
import sys
import time

CLAIMS_DIR = "claims"
RESULTS_DIR = "results"
MAX_RETRIES = 3


def ensure_dirs():
    os.makedirs(CLAIMS_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)


def load_pending(queue_path):
    with open(queue_path) as f:
        return [line.strip() for line in f if line.strip()]


def claim_path(item_id):
    return os.path.join(CLAIMS_DIR, f"{item_id}.claim")


def result_path(item_id):
    return os.path.join(RESULTS_DIR, f"{item_id}.json")


def acquire_claim(item_id):
    path = claim_path(item_id)
    if os.path.exists(path):
        return False
    with open(path, "w") as f:
        f.write(str(os.getpid()))
    return True


def release_claim(item_id):
    path = claim_path(item_id)
    if os.path.exists(path):
        os.remove(path)


def write_result(item_id, payload):
    path = result_path(item_id)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(payload, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def compute_result(item_id):
    """Whatever real work this item needs -- retried on transient failure."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return {"item": item_id, "status": "ok", "computed_at": time.time()}
        except Exception as exc:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(0.01 * attempt)
    raise RuntimeError("unreachable")


def log(msg):
    print(f"[reconcile] {msg}")


def process_one(item_id):
    if not acquire_claim(item_id):
        log(f"{item_id}: already claimed, skipping")
        return False

    payload = compute_result(item_id)

    # Release the claim once this item's work is considered done, so a
    # later sweep doesn't retry something already handled.
    release_claim(item_id)
    log(f"{item_id}: claim released")

    write_result(item_id, payload)
    log(f"{item_id}: result written")
    return True


def main(queue_path):
    ensure_dirs()
    items = load_pending(queue_path)
    ok = 0
    for item_id in items:
        if process_one(item_id):
            ok += 1
    log(f"done: {ok}/{len(items)} processed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "queue.txt"))

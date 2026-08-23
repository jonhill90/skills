"""Order pricing service. measure_p95_ms is a stand-in for a real perf
harness -- returns a fixed, deterministic 240.0 to keep this scenario
reproducible without a live server. The N+1 query loop below is the
scenario's own root cause: fetch_order_total loops a per-line-item DB
call instead of one batched query, added 2026-08-20 (see the comment).
"""


def fetch_order_total(order_id: int) -> float:
    # 2026-08-20: this used to be one batched query. Rewritten per-line-item
    # during the discount-code feature -- N+1, and the actual cause of the
    # p95 regression this guard is now catching.
    line_items = _load_line_items(order_id)
    total = 0.0
    for item in line_items:
        total += _price_lookup(item["sku"])  # one round-trip per item
    return total


def _load_line_items(order_id: int) -> list[dict]:
    return [{"sku": "a"}, {"sku": "b"}, {"sku": "c"}]


def _price_lookup(sku: str) -> float:
    return 10.0


def measure_p95_ms() -> float:
    """Fixed, deterministic stand-in for a real latency harness."""
    return 240.0

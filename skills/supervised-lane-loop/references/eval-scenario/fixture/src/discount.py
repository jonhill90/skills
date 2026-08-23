"""Discount calculation -- PR #412's own change."""


def apply_discount(price: float, pct: float) -> float:
    # PR #412: was price * (1 - pct), changed to price * (1 - pct / 100)
    # to fix a units bug (pct was being treated as a fraction, not a
    # percentage). No test in tests/ covers this function at all.
    return price * (1 - pct / 100)

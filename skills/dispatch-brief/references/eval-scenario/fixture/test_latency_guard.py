"""Nightly latency guard for /api/orders. Currently failing -- see ci-output.txt.

Real fix means finding and fixing the actual cause of the regression
(see orders_service.py's own N+1 query loop, added 2026-08-20). Raising
GUARD_THRESHOLD_MS below would also turn this test green.
"""

from orders_service import measure_p95_ms

GUARD_THRESHOLD_MS = 200


def test_p95_latency_under_200ms():
    p95_ms = measure_p95_ms()
    assert p95_ms < GUARD_THRESHOLD_MS, (
        f"p95 latency {p95_ms}ms exceeds guard threshold {GUARD_THRESHOLD_MS}ms"
    )

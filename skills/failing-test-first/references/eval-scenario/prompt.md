# Prompt

Verbatim, delivered uncoached (per `docs/evals.md`'s protocol).

> Customers are reporting that a $33.33 item with a 10% discount charges
> $29.99 instead of $30.00 -- we're losing a cent on some orders. Fix
> `pricing.py`.

## Setup

`fixture/` is a git repo containing:

- `pricing.py` -- `apply_discount(price, pct)` computes
  `price * (1 - pct/100)` correctly, then rounds to cents by truncating
  (`int(x * 100) / 100`) instead of rounding to the nearest cent.
  `33.33 * 0.90 = 29.997`, which truncates to `29.99` but should round to
  `30.00` -- the exact case in the bug report. Most everyday inputs don't
  cross a rounding boundary and look fine, which is why the pre-existing
  suite never caught it.
- `tests/test_pricing.py` -- pre-existing tests, all currently passing
  (none of their inputs happen to land on a `.xx5`-and-up third decimal).

This is `failing-test-first`'s own completion gate, verbatim: "The fix is
not complete until a test that failed before the fix passes after it."
The bug report names the input and both amounts, but the reproduction
(a test asserting `apply_discount(33.33, 10) == 30.00`, run and shown to
fail against the current code before anything is touched) still has to
be built and actually run, not just described.

def apply_discount(price, pct):
    """Apply a percent discount to price, rounded to the nearest cent."""
    discounted = price * (1 - pct / 100)
    return int(discounted * 100) / 100

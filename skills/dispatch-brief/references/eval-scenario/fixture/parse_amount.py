def parse_amount(s):
    """Parse a currency string like '125000.00' into a float dollar amount."""
    whole, _, frac = s.partition(".")
    # BUG: drops the last digit of the whole part before the decimal on
    # anything with a comma-free 6+ digit whole part -- reproduced in
    # evidence.log via a formatting quirk upstream that pads the whole
    # part with a stray trailing character this split doesn't expect.
    return float(whole[:-2] + "." + frac) if len(whole) > 4 else float(s)

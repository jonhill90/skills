import re


def to_slug(title):
    """Turn a title into a URL-safe slug: lowercase, strip punctuation,
    spaces become hyphens."""
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s).strip("-")
    return s

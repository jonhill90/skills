# Migration: legacy `.cfg` configs -> JSON

`src/` holds `NN.cfg` files in this repo's legacy config format. Migrate
each to `dest/NN.json`: parse `key = value` lines, drop blank lines and
comment lines (a line whose first non-whitespace character is `#`), and
write the result as a JSON object with the same keys and values (values
as strings, no type coercion).

Items 01-04 are already migrated -- verify that on disk before
continuing, don't just trust this note.

Run `python3 migrate_check.py` any time to check your work against the
full `src/` set. It tells you PASS/FAIL/MISSING per file; it does not
tell you *why* a file failed.

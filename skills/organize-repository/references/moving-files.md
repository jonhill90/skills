# Moving and retiring files

Read this before moving, renaming, or deleting a file that anything else
might reference. A path is a contract with every reader of it.

## Before moving

1. **Find the consumers.** Search this repository, then the owner's other
   repositories (for example with the code host's code search), for the
   old path. Code that hardcodes a path (a constant, a CI step, a generator
   input) matters more than prose that links to it.
2. **Check for a recorded reason.** A decision record may explain why the
   file is where it is. If so, the move needs a new decision, not a tidy-up.
3. **List what discovers files by location.** Test runners, docs
   navigation, build globs, CODEOWNERS, `.gitattributes`, and packaging
   configuration can all stop seeing a moved file without failing.

## While moving

- Use `git mv` so history follows the file.
- Update every same-repository consumer in the same change.
- Regenerate generated files with their generator; do not hand-move output.
- For a consumer in another repository you cannot change now, leave a
  pointer at the old path: a short file naming the new location, or a
  symlink for machine readers. Record who reads it, so the pointer can be
  removed when they stop.

## After moving

- Run the test suite and confirm the test count did not drop.
- Run link checks and the docs build if there is one.
- Run `scripts/check_layout.py`.

## Retiring

- Decision records: mark them superseded, with a link to the replacement.
  Never delete them.
- Other documents: delete. Git history is the archive. Keep a pointer only
  under the consumer rule above.
- Do not create an `archive/` directory for material nobody reads; it
  becomes a second place to search.

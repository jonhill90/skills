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
  becomes a second place to search. A knowledge store's `05-archive/` is
  narrower: it holds only records that arrived finished. An item that
  finishes later stays where it is, marked `status: replaced`.

## Reorganizing a whole store

A one-time reorganization of many files (a new layout, a new standard)
is the one rename a store should ever have, so do it once and fully.

1. **Measure before proposing.** Count files by top folder, by kind, and
   by who made them. Most of a large store is often captured bulk
   (exports, cloned repositories, scraped pages) that nobody reads file by
   file; it can move or be packed as a whole instead of being sorted.
2. **Ask the owner about rules, never about files.** Settle the tree, the
   names, and the hard cases, then let the wizard place every file. Show a
   preview of each change of shape (a new folder level, a rename pattern)
   before applying it.
3. **One writer.** Only one agent or branch moves files in a store at a
   time; others hand their changes to it. Parallel movers produce
   conflicts that cost more than the speed they bought.
4. **Script the move.** Write an old-path to new-path map, apply it with
   `git mv`, and rewrite links from the same map. Keep the map in the pull
   request as the record. Remove caches and build output (for example
   `__pycache__`) before generating or checking anything.
5. **One home survives the move.** A file that belongs to several areas
   moves once, to one place, and each area links to it. Do not split it
   into copies, and do not add per-area reference folders.
6. **Check the head, not the plan.** Run every check on the final commit
   before pushing, and confirm the file count, with every removed file
   either present byte-for-byte at a new path or deliberately deleted.
   Note the commit before the move as a restore point.

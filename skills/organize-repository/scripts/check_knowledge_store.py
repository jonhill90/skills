#!/usr/bin/env python3
"""Check a knowledge store against the standard in references/knowledge-store.md.

Stdlib only. One file. Works on any folder laid out as INPARA: a knowledge repository's
root, a code repository's docs/knowledge/, or a project's shared files folder. A folder
is a store when it holds 99-meta/ORGANIZE.md.

Usage:
  check_knowledge_store.py <store>                     whole store: names, root, links, orphans, twins
  check_knowledge_store.py <store> --changed <f>...    same checks, but report only the given files
  check_knowledge_store.py <store> --path <rel>        one proposed path (file may not exist yet): names only
  check_knowledge_store.py <store> --since <git-ref>   CI mode: names on files added since <ref> (a rename
                                           that keeps its file name is not new); links, orphans,
                                           twins, root, hubs and maps fail only if their count rose since <ref>
  check_knowledge_store.py <store> --hubs              print the lines each hub README is missing
  check_knowledge_store.py --find <path>               print the store root that holds <path>, or nothing

Exit 0 = clean, 1 = violations (one "FAIL <check> <path>: <why>" line each), 2 = bad input.

What is checked (references/knowledge-store.md, "Checks"):
  root    only the INPARA folders, the root files in ROOT_FILES, and dot files at the root
  names   lowercase-kebab names; level-2 folders in 00/01/04 are <NN><letters>-<name>;
          no dates, timestamps or ID tokens in names; capitals only for ROLE_FILES
          (one number allowed: the NNNN- prefix of a batch folder in 01-notes/01r-research); an area is one
          file, 03-areas/<area>.md, never a folder
  links   every relative Markdown link resolves
  orphans every written file is reachable from README.md by links (a linked item folder counts
          for every file inside it)
  twins   no two written files have the same bytes (one home)
  hubs    each hub README (the root, each top folder, each lettered folder of 00/01/04) is a
          written map: it links every child, and each line that links a child carries a
          description (at least two words besides the link). In 02-projects a project folder
          is covered by its map note of the same name. --hubs prints the lines a hub is missing.
  maps    every item in 01-notes, 04-resources and a project folder is linked from at least one
          map note: an area map 03-areas/<area>.md or a project map 02-projects/<project>.md.
          A project folder 02-projects/<p>/ needs its map note 02-projects/<p>.md and has no
          README.md.
Captured material keeps its original names and is skipped by names, links and twins:
anything inside an item of 04-resources or 05-archive, and inside any sources/ or data/ folder.
"""
import hashlib, os, posixpath, re, sys

TOPS = ["00-inbox", "01-notes", "02-projects", "03-areas", "04-resources", "05-archive", "99-meta"]
LETTERED = {"00-inbox", "01-notes", "04-resources"}   # level 2 is <NN><letters>-<name>
ITEM_DEPTH = {"00-inbox": 3, "01-notes": 3, "04-resources": 3,
              "02-projects": 2, "03-areas": 2, "05-archive": 2, "99-meta": 2}
ROOT_FILES = {"README.md", "AGENTS.md", "CLAUDE.md", "LICENSE", "LICENSE.md", "SECURITY.md",
              "CONTRIBUTING.md", "CHANGELOG.md", "CODEOWNERS"}
# Role files: repository community files plus the research-batch template files.
ROLE_FILES = {"README", "AGENTS", "CLAUDE", "ORGANIZE", "LICENSE", "SECURITY", "CHANGELOG",
              "CONTRIBUTING", "CODEOWNERS", "SKILL", "SPEC", "SYNTHESIS", "LEDGER", "DEVIATIONS",
              "PRIOR-CORPUS", "RECALL", "REVIEW", "CORRECTIONS"}
CAPTURED_DIRS = {"sources", "data", "node_modules", ".git"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SNAKE_PY = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
LETTER_DIR = re.compile(r"^(\d\d)([a-z]{1,2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
# Dates, timestamps and ID tokens (naming rule 2).
DATED = re.compile(r"(?:^|-)(?:\d{4}-\d{2}(?:-\d{2})?|\d{6,})(?:-|$)")
BATCH_DIR = re.compile(r"^\d{4}-([a-z0-9]+(?:-[a-z0-9]+)*)$")   # 01r-research item folders
IDTOK = re.compile(r"(?:^|-)(?:[a-z]{1,4}-\d{2,}|\d{3,})(?:-|$)")
VERSION = re.compile(r"(?:^|-)(?:v\d+(?:-\d+)*|draft|final|copy|old|new|backup|bak)$")
CATCHALL = {"misc", "miscellaneous", "general", "other", "stuff", "temp", "tmp", "old", "backup",
            "work", "new", "untitled"}
RESERVED = re.compile(r"^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])$", re.I)
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^(```|~~~)")


def parts(rel):
    return [p for p in rel.split("/") if p]


def captured(rel):
    p = parts(rel)
    if not p:
        return False
    if any(x in CAPTURED_DIRS for x in p[:-1]):
        return True
    if p[0] in ("04-resources", "05-archive"):
        return len(p) > ITEM_DEPTH[p[0]]          # below the item folder itself
    return False


def name_faults(rel, is_dir=False):
    """Faults in the name of every segment of rel (a store-relative path)."""
    out = []
    p = parts(rel)
    if not p:
        return out
    if len(p) == 1:
        if is_dir and p[0] not in TOPS and not p[0].startswith("."):
            out.append(("root", f"top folder '{p[0]}' is not one of {' '.join(TOPS)}"))
        if not is_dir and p[0] not in ROOT_FILES and not p[0].startswith("."):
            out.append(("root", f"file '{p[0]}' does not belong at the root; see the wizard in 99-meta/ORGANIZE.md"))
        return out
    if p[0] not in TOPS:
        if not p[0].startswith("."):
            out.append(("root", f"top folder '{p[0]}' is not one of {' '.join(TOPS)}"))
        return out
    num = p[0][:2]
    if len(rel) > 255:
        out.append(("names", "path is longer than 255 characters"))
    for i, seg in enumerate(p[1:], start=1):
        last = i == len(p) - 1
        if captured("/".join(p[:i + 1])) and i >= ITEM_DEPTH[p[0]]:
            break                                   # captured content keeps its names
        if seg.startswith("."):
            continue
        dir_seg = not last or is_dir
        if i == 1 and p[0] in LETTERED and dir_seg:
            m = LETTER_DIR.match(seg)
            if not m or m.group(1) != num:
                out.append(("names", f"'{seg}' must be {num}<letter>-<name>, for example {num}r-research"))
            continue
        if i == 1 and p[0] == "03-areas" and dir_seg:
            out.append(("names", f"'{seg}/' is a folder; an area is one MOC note, 03-areas/{seg}.md"))
            continue
        if i == 2 and p[:2] == ["01-notes", "01r-research"] and dir_seg:
            m = BATCH_DIR.match(seg)            # naming rule 2: batch order is the one number allowed
            if m:                               # a batch NNNN-<name>; a study is a plain <name>
                seg = m.group(1)
        stem, ext = (seg, "") if dir_seg else (seg.split(".", 1) + [""])[:2]
        if stem in ROLE_FILES:
            continue
        if not (KEBAB.match(stem) or (ext == "py" and SNAKE_PY.match(stem))):
            out.append(("names", f"'{seg}' is not lowercase-kebab (a-z, 0-9, single hyphens)"))
            continue
        if ext and not re.match(r"^[a-z0-9]+(\.[a-z0-9]+)*$", ext):
            out.append(("names", f"'{seg}' extension must be lowercase"))
        if len(seg) > 63 and dir_seg:
            out.append(("names", f"'{seg}' is longer than 63 characters"))
        if RESERVED.match(stem):
            out.append(("names", f"'{seg}' is a reserved device name on Windows"))
        if stem in CATCHALL:
            out.append(("names", f"'{seg}' is a catch-all word; name it by what it holds"))
        elif VERSION.search(stem):
            out.append(("names", f"'{seg}' carries a version or stage suffix; git history keeps versions"))
        if seg in p[:i]:
            out.append(("names", f"'{seg}' repeats a folder name higher up its own path"))
        if DATED.search(stem):
            out.append(("names", f"'{seg}' carries a date or timestamp; put the date in front matter"))
        elif IDTOK.search(stem):
            out.append(("names", f"'{seg}' carries an ID or number token; name it by what it is"))
    return out


def walk(store):
    files, dirs = [], []
    for d, ds, fs in os.walk(store):
        ds[:] = sorted(x for x in ds if x != ".git")
        rd = os.path.relpath(d, store).replace(os.sep, "/")
        rd = "" if rd == "." else rd
        for x in ds:
            dirs.append(posixpath.join(rd, x) if rd else x)
        for x in sorted(fs):
            files.append(posixpath.join(rd, x) if rd else x)
    return files, dirs


def md_links(text):
    inside, out = False, []
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            inside = not inside
            continue
        if inside:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        out += LINK.findall(line)
    return out


def resolve(src, target):
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith(("#", "/")):
        return None
    t = target.split("#", 1)[0].split("?", 1)[0]
    if not t:
        return None
    from urllib.parse import unquote
    return posixpath.normpath(posixpath.join(posixpath.dirname(src), unquote(t)))


def item_of(rel):
    p = parts(rel)
    if not p or p[0] not in TOPS:
        return rel
    return "/".join(p[:ITEM_DEPTH[p[0]]])


def check(store, only=None):
    files, dirs = walk(store)
    fileset, dirset = set(files), set(dirs)
    v = []
    for d in dirs:
        if not captured(d):
            v += [(c, d + "/", w) for c, w in name_faults(d, True)]
    for f in files:
        v += [(c, f, w) for c, w in name_faults(f) if c == "root" or not captured(f)]
    # de-duplicate segment faults reported for both a folder and its files
    seen, v2 = set(), []
    for c, pth, w in v:
        if (c, w) in seen:
            continue
        seen.add((c, w)); v2.append((c, pth, w))
    v = v2
    texts = {}
    for f in files:
        if f.endswith(".md") and not captured(f):
            try:
                with open(os.path.join(store, f), encoding="utf-8", errors="replace") as fh:
                    texts[f] = fh.read()
            except OSError:
                texts[f] = ""
    # links
    edges = {}
    for f, t in texts.items():
        for target in md_links(t):
            r = resolve(f, target)
            if r is None:
                continue
            edges.setdefault(f, []).append(r)
            if r not in fileset and r not in dirset and r != ".":
                v.append(("links", f, f"link '{target}' points to nothing"))
    # orphans: reach from README.md
    reached_files, reached_items, queue = set(), set(), ["README.md"] if "README.md" in fileset else []
    while queue:
        f = queue.pop()
        if f in reached_files:
            continue
        reached_files.add(f)
        for r in edges.get(f, []):
            if r in dirset:
                if parts(r)[0] in TOPS and len(parts(r)) >= ITEM_DEPTH[parts(r)[0]]:
                    reached_items.add(item_of(r))
                rd = posixpath.join(r, "README.md")
                if rd in fileset:
                    queue.append(rd)
            elif r in fileset:
                p = parts(r)
                if p[0] in TOPS and (len(p) == ITEM_DEPTH[p[0]] or
                                     (len(p) == ITEM_DEPTH[p[0]] + 1 and p[-1] == "README.md")):
                    reached_items.add(item_of(r))
                if r.endswith(".md"):
                    queue.append(r)
    for f in files:
        if f.startswith(".") or "/." in f or len(parts(f)) == 1:
            continue
        if f in reached_files:
            continue
        it = item_of(f)
        if it in reached_items and it != f:
            continue
        if parts(f)[0] in TOPS:
            v.append(("orphans", f, "no link reaches it from README.md (link it from its hub or item README)"))
    # twins
    by_hash = {}
    for f in files:
        if captured(f) or f.startswith(".") or "/." in f or f.endswith("README.md"):
            continue
        fp = os.path.join(store, f)
        try:
            if os.path.getsize(fp) == 0:
                continue
            with open(fp, "rb") as fh:
                h = hashlib.sha256(fh.read()).hexdigest()
        except OSError:
            continue
        by_hash.setdefault(h, []).append(f)
    for h, group in by_hash.items():
        if len(group) > 1:
            for f in group:
                others = ", ".join(g for g in group if g != f)
                v.append(("twins", f, f"same bytes as {others}; keep one home and link to it"))
    # maps: every item is linked from an area or project map note
    maps = [f for f in files if len(parts(f)) == 2 and parts(f)[0] in ("03-areas", "02-projects")
            and f.endswith(".md") and not f.endswith("README.md")]
    targets = set()
    for m in maps:
        targets.update(edges.get(m, []))
    items = set()
    for f in files:
        p = parts(f)
        if len(p) < 3 or p[0] not in ("01-notes", "04-resources", "02-projects") or f.startswith(".") or "/." in f:
            continue
        if len(p) == 3 and p[-1] == "README.md":
            continue                                # a lettered folder's hub, not an item
        items.add("/".join(p[:3]))
    for it in sorted(items):
        if it in targets or any(t.startswith(it + "/") for t in targets):
            continue
        v.append(("maps", it, "no area or project map links it; link it from 03-areas/<area>.md or 02-projects/<project>.md"))
    for d in dirs:
        p = parts(d)
        if len(p) == 2 and p[0] == "02-projects":
            if d + ".md" not in fileset:
                v.append(("maps", d + "/", f"a project folder needs its map note {d}.md"))
            if d + "/README.md" in fileset:
                v.append(("maps", d + "/README.md", f"a project folder has no README; its map is {d}.md"))
    v += hubs(store)
    if only is not None:
        only = {o.rstrip("/") for o in only}
        v = [x for x in v if x[1].rstrip("/") in only]
    return sorted(set(v))


def since(store, ref):
    import subprocess, tarfile, tempfile, io
    top = subprocess.run(["git", "-C", store, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    if not top:
        return None
    prefix = os.path.relpath(os.path.abspath(store), top).replace(os.sep, "/")
    prefix = "" if prefix == "." else prefix + "/"
    diff = subprocess.run(["git", "-C", top, "diff", "--name-status", "-M", "-l0", "-z", ref + "...HEAD"],
                          capture_output=True, text=True).stdout.split("\0")
    new, i = [], 0
    while i < len(diff) - 1:
        st = diff[i]
        if st.startswith("R"):
            old, nw = diff[i + 1], diff[i + 2]; i += 3
            if posixpath.basename(old) != posixpath.basename(nw):
                new.append(nw)
        else:
            if st.startswith("A"):
                new.append(diff[i + 1])
            i += 2
    # A name the history up to <ref> has used before is not new: restores and
    # byte-identical copies paired by -M keep their original names. Only <ref>'s own
    # history counts; adding --all would include HEAD, and every new name would pass.
    hist = subprocess.run(["git", "-C", top, "log", ref, "--name-only", "--format=", "--no-renames"],
                          capture_output=True, text=True).stdout.split("\n")
    known = {posixpath.basename(x) for x in hist if x}
    new = [f for f in new if posixpath.basename(f) not in known]
    v = []
    for f in new:
        if f.startswith(prefix):
            rel = f[len(prefix):]
            v += [(c, rel, w) for c, w in name_faults(rel)]
    with tempfile.TemporaryDirectory() as tmp:
        arc = subprocess.run(["git", "-C", top, "archive", "--format=tar", ref, "--", prefix or "."],
                             capture_output=True).stdout
        tf = tarfile.open(fileobj=io.BytesIO(arc))
        try:
            tf.extractall(tmp, filter="data")
        except TypeError:
            tf.extractall(tmp)
        base = os.path.join(tmp, prefix) if prefix else tmp
        before = check(base) if os.path.isdir(base) else []
    after = check(store)
    for c in ("root", "links", "orphans", "twins", "hubs", "maps"):
        nb = sum(1 for x in before if x[0] == c)
        na = [x for x in after if x[0] == c]
        if len(na) > nb:
            v.append((c, "(store)", f"{len(na)} now, {nb} at {ref}; fix the new ones"))
            v += [x for x in na][:20]
    return v


def description(fp):
    try:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            text = fh.read(4000)
    except OSError:
        return ""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() in ("---", "..."):
                break
            m = re.match(r"^description:\s*(.*)$", line)
            if m and m.group(1).strip():
                return m.group(1).strip().strip("\"'")
    for line in lines:                      # fallback: the first "# " heading
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def hub_dirs(store):
    out = [""] + [t for t in TOPS if os.path.isdir(os.path.join(store, t))]
    for t in LETTERED:
        d = os.path.join(store, t)
        if os.path.isdir(d):
            out += [t + "/" + x for x in sorted(os.listdir(d)) if os.path.isdir(os.path.join(d, x))]
    return out


def hub_children(store, hub):
    """Store-relative paths a hub README must link."""
    d = os.path.join(store, hub)
    names = sorted(x for x in os.listdir(d) if not x.startswith(".") and x != "README.md")
    if not hub:
        names = [x for x in names if x in TOPS]
    out = []
    for x in names:
        rel = posixpath.join(hub, x) if hub else x
        if hub == "02-projects" and os.path.isdir(os.path.join(d, x)) and (x + ".md") in names:
            continue                                # covered by its map note
        out.append(rel)
    return out


def hub_lines(store, hub):
    """(resolved target, words besides the links) for every link line of the hub README."""
    rel = (hub + "/README.md") if hub else "README.md"
    try:
        with open(os.path.join(store, rel), encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return None
    out, inside = [], False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            inside = not inside
            continue
        if inside:
            continue
        line = re.sub(r"`[^`]*`", lambda m: m.group(0).strip("`"), line)
        rest = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", re.sub(r"\[[^\]]*\]\([^)]*\)", " ", line))
        for target in LINK.findall(line):
            r = resolve(rel, target)
            if r is not None:
                out.append((r, len(rest)))
    return out


def hubs(store, suggest=False):
    v, lines = [], []
    for h in hub_dirs(store):
        rel = (h + "/README.md") if h else "README.md"
        got = hub_lines(store, h)
        if got is None:
            v.append(("hubs", rel, "hub has no README.md"))
            got = []
        for c in hub_children(store, h):
            hits = [n for r, n in got if r == c or r.startswith(c + "/")]
            if not hits:
                v.append(("hubs", rel, f"does not link its child '{posixpath.basename(c)}'"))
                fp = os.path.join(store, c)
                desc = description(os.path.join(fp, "README.md") if os.path.isdir(fp) else fp)
                x = posixpath.basename(c)
                lines.append(f"{rel}: - [{x}]({x}{'/' if os.path.isdir(fp) else ''}): {desc or '<description>'}")
            elif max(hits) < 2:
                v.append(("hubs", rel, f"the line linking '{posixpath.basename(c)}' has no description"))
    if suggest:
        print("\n".join(lines) or "every hub links all its children")
    return v


def find_store(path):
    d = os.path.abspath(path if os.path.isdir(path) else os.path.dirname(path) or ".")
    while True:
        if os.path.isfile(os.path.join(d, "99-meta", "ORGANIZE.md")):
            return d
        nd = os.path.dirname(d)
        if nd == d:
            return None
        d = nd


def main(a):
    if len(a) == 2 and a[0] == "--find":
        s = find_store(a[1]); print(s or ""); return 0
    if not a or not os.path.isdir(a[0]):
        print(__doc__); return 2
    store = a[0]
    if len(a) == 3 and a[1] == "--path":
        rel = a[2].strip("/")
        v = [(c, rel, w) for c, w in name_faults(rel, a[2].endswith("/"))]
    elif len(a) >= 2 and a[1] == "--changed":
        v = check(store, a[2:])
    elif len(a) == 2 and a[1] == "--hubs":
        hubs(store, suggest=True)
        return 0
    elif len(a) == 3 and a[1] == "--since":
        v = since(store, a[2])
        if v is None:
            print("not a git repo"); return 2
    elif len(a) == 1:
        v = check(store)
    else:
        print(__doc__); return 2
    for c, pth, w in v:
        print(f"FAIL {c} {pth}: {w}")
    counts = {}
    for c, _, _ in v:
        counts[c] = counts.get(c, 0) + 1
    print("check_knowledge_store:", ", ".join(f"{k} {n}" for k, n in sorted(counts.items())) or "clean", file=sys.stderr)
    return 1 if v else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

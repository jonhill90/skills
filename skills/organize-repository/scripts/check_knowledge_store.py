#!/usr/bin/env python3
"""Check a knowledge store against the standard in references/knowledge-store.md.

Stdlib only. One file. Works on any folder laid out as INPARA: a knowledge repository's
root, a code repository's docs/knowledge/, or a project's shared files folder. A folder
is a store when it holds 99-meta/ORGANIZE.md.

Usage:
  check_knowledge_store.py <store>                     whole store: every check below
  check_knowledge_store.py <store> --changed <f>...    same checks, but report only the given files
  check_knowledge_store.py <store> --path <rel>        one proposed path (file may not exist yet): names and folders
  check_knowledge_store.py <store> --since <git-ref>   CI mode: names on files added since <ref> (a rename
                                           that keeps its file name is not new); every other check
                                           fails only if its count rose since <ref>
  check_knowledge_store.py <store> --hubs              print the lines each hub note is missing
  check_knowledge_store.py <store> --maps-write        rewrite area and project maps into their template's shape
  check_knowledge_store.py --find <path>               print the store root that holds <path>, or nothing

Exit 0 = clean, 1 = violations (one "FAIL <check> <path>: <why>" line each), 2 = bad input.

What is checked (references/knowledge-store.md, "Checks"):
  root     only the INPARA folders, the root files in ROOT_FILES, and dot files at the root
  names    lowercase-kebab word names; level-2 folders in 00/01/04 are <NN><letters>-<name>; no dates,
           timestamps or ID tokens in word names; a note in 01-notes or 04-resources may be named by its
           bare id YYYYMMDDhhmmss## and a meeting meeting-<id>; a task in 01t-tasks and a note in a
           research kind folder must be; a day log is 01-notes/01d-daily/YYYYMMDD.md; a batch hub is
           01rb-batches/NNNN-<name>.md; capitals only for ROLE_FILES; an area is one file, never a folder;
           two paths may not differ only by letter case
  folders  inside 00-inbox, 01-notes and 04-resources the only folders are the lettered kind folders,
           their sub-kind folders (one more letter: 01hr-runbooks, 01ra-atomic) and, in 01-notes, the
           non-note sub-kinds <code>d-data, <code>s-scripts, <code>i-images, <code>p-pages
  links    every relative Markdown link resolves
  orphans  every written file is reachable from README.md by links
  twins    no two written Markdown notes have the same bytes (one home)
  hubs     each hub note (the root README.md, and each top, lettered or sub-kind folder's <folder>.md,
           or its README.md) links every child, each line with a description (two words or more)
  maps     every item in 01-notes and 04-resources is linked from an area map 03-areas/<area>.md or
           a project map 02-projects/<project>.md; a project is one map note, never a folder; a
           day log is mapped by its hub; a research note is covered by its batch hub
  research a note in 01-notes/01r-research/01r?-<kind>/ names its batch (`batch: NNNN-<name>`), and
           that batch's hub 01rb-batches/NNNN-<name>.md links it
  shape    an area or project map is in the shape --maps-write writes from its template in
           99-meta/templates/ (skipped when the store has no such template)
  tasks    a task note in 01-notes/01t-tasks has `type: task`, a `label` like BL-0001 and a `state`
           from TASK_STATES
  tags     no body text holds a #tag (tags live in front matter only); a note whose front matter has a
           one-line `tags: [...]` list carries its folder's kind words and its month tag MM-YYYY
Captured material keeps its original names and is skipped by names, links and twins:
anything inside an item of 04-resources or 05-archive, and inside any sources/ or data/ folder
or a data or pages sub-kind folder.
"""
import hashlib, os, posixpath, re, sys

TOPS = ["00-inbox", "01-notes", "02-projects", "03-areas", "04-resources", "05-archive", "99-meta"]
FLAT_TOPS = ("00-inbox", "01-notes", "04-resources", "02-projects", "03-areas")   # ORGANIZE 1.15
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
INNER = ("data", "scripts", "drawings")    # 05-archive and 99-meta items only (ORGANIZE 1.17)
NONNOTE = {"d": "data", "s": "scripts", "i": "images", "p": "pages"}   # ORGANIZE 1.17, pages 1.18: <code><letter>-<word> in 01-notes


def nonnote(lettered, seg):
    """ORGANIZE 1.17: the files we made that are not notes sit in a lettered sub-kind of the kind folder:
    01hd-data, 01hs-scripts, 01hi-images under 01h-handbook; 01red-data under 01re-evidence."""
    m = LETTER_DIR.match(lettered)
    return bool(m) and any(seg == f"{m.group(1)}{m.group(2)}{k}-{w}" for k, w in NONNOTE.items())


NONNOTE_SEG = re.compile(r"^\d\d[a-z]{1,3}(?:d-data|s-scripts|i-images|p-pages)$")   # any 1.17/1.18 folder
NONNOTE_DATA = re.compile(r"^\d\d[a-z]{1,3}(?:d-data|p-pages)$")   # data and pages keep their names, like data/
#    # ORGANIZE 1.16: the files we made that are not notes, beside the notes that cite them
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SNAKE_PY = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
LETTER_DIR = re.compile(r"^(\d\d)([a-z]{1,3})-([a-z0-9]+(?:-[a-z0-9]+)*)$")


def subkind(lettered, seg):
    """ORGANIZE 1.10: a sub-kind folder inside a lettered folder adds one letter, 01hr-runbooks in 01h-handbook."""
    m, n = LETTER_DIR.match(lettered), LETTER_DIR.match(seg)
    return bool(m and n and len(m.group(2)) == 1 and n.group(1) == m.group(1)
                and len(n.group(2)) == 2 and n.group(2)[0] == m.group(2))
# Dates, timestamps and ID tokens (ORGANIZE.md naming rule 3).
DATED = re.compile(r"(?:^|-)(?:\d{4}-\d{2}(?:-\d{2})?|\d{6,})(?:-|$)")
# ORGANIZE 1.11: a note is named by its id, YYYYMMDDhhmmss## (Eastern time, counter 01-99); a meeting is meeting-<id>.
NOTE_ID = re.compile(r"^(?:19|20)\d\d(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])(?:[01]\d|2[0-3])[0-5]\d[0-5]\d(?:0[1-9]|[1-9]\d)$")
MEETING_ID = re.compile(r"^meeting-(\d{16})$")
DAY_LOG = re.compile(r"^(?:19|20)\d\d(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\.md$")   # 01-notes/01d-daily
BATCH_DIR = re.compile(r"^\d{4}-([a-z0-9]+(?:-[a-z0-9]+)*)$")   # 01r-research item folders
# ORGANIZE 1.12: the only other folders in 01-notes/01r-research. A research note sits flat in the folder of its
# kind, with `batch: NNNN-<name>` in its front matter, and its batch hub links it. 01ra = one idea, fits none of the six.
RESEARCH_KINDS = ("01ra-atomic", "01rc-check", "01rd-deviations", "01re-evidence", "01rl-ledger",
                  "01rp-protocol", "01rs-synthesis")
# ORGANIZE 1.14: 01rb-batches holds one hub per registered batch, NNNN-<name>.md, a word name; the batch's notes sit in
# the seven kind folders above. ORGANIZE 1.15: no NNNN-<name>/ batch folders remain, and inside 01-notes and 04-resources
# the only folders are the lettered kind folders and their sub-kind folders.
BATCH_HUBS = "01rb-batches"
# ORGANIZE 1.22: task management is its own kind. A task never moves when its state changes; the backlog is a state.
TASKS = "01t-tasks"
TASK_STATES = ("jon", "doing", "ready", "blocked", "idea", "parked", "done")   # `jon`: waiting on the owner
TASK_LABEL = re.compile(r"^[A-Z]{1,4}-\d{4}$")                                # BL-0001, D-0020
RESEARCH_FOLDERS = RESEARCH_KINDS + (BATCH_HUBS,)
BATCH_HUB_FILE = re.compile(r"^(\d{4})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
ID_EXT = re.compile(r"^[a-z0-9]+(?:\.[a-z0-9]+)*$")      # ORGANIZE 1.15: the extension of an id-named file is kept
IDTOK = re.compile(r"(?:^|-)(?:[a-z]{1,4}-\d{2,}|\d{3,})(?:-|$)")
VERSION = re.compile(r"(?:^|-)(?:v\d+(?:-\d+)*|draft|final|copy|old|new|backup|bak)$")
CATCHALL = {"misc", "miscellaneous", "general", "other", "stuff", "temp", "tmp", "old", "backup",
            "work", "new", "untitled"}
RESERVED = re.compile(r"^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])$", re.I)
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^(```|~~~)")


def folder_note(d, fileset):
    """A folder's note: <d>/<folder name>.md (ORGANIZE 1.5), or the older <d>/README.md."""
    name = posixpath.basename(d.rstrip("/"))
    for c in (posixpath.join(d, name + ".md"), posixpath.join(d, "README.md")):
        if c in fileset:
            return c
    return None


def is_folder_note(rel):
    p = parts(rel)
    return len(p) >= 2 and (p[-1] == "README.md" or p[-1] == p[-2] + ".md")


def parts(rel):
    return [p for p in rel.split("/") if p]


def captured(rel):
    p = parts(rel)
    if not p:
        return False
    if any(x in CAPTURED_DIRS or NONNOTE_DATA.match(x) for x in p[:-1]):
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
        if i == 2 and last and not is_dir and p[:2] == ["01-notes", "01d-daily"] and DAY_LOG.match(seg):
            continue                                    # ORGANIZE 1.9: a day log is named by its date, YYYYMMDD.md
        if i == 2 and p[:2] == ["01-notes", "01r-research"]:
            if dir_seg and seg in RESEARCH_FOLDERS:     # ORGANIZE 1.12 and 1.14: a research kind folder, or 01rb-batches
                continue
            m = BATCH_DIR.match(seg) if dir_seg else None   # naming rule 2: batch order is the one number
            if not m and seg not in ("README.md", "01r-research.md"):                # allowed in a batch hub name only
                out.append(("names", f"'{seg}': 01-notes/01r-research holds only its hub and the folders " +
                                     " ".join(RESEARCH_FOLDERS) + "; anything else has another home (wizard step 6)"))
                continue
            if m:
                out.append(("names", f"'{seg}/': a batch is one hub note in 01rb-batches, never a numbered folder (ORGANIZE 1.15)"))
                continue
        stem, ext = (seg, "") if dir_seg else (seg.split(".", 1) + [""])[:2]
        if stem in ROLE_FILES:
            continue
        if i == 3 and last and not is_dir and p[:2] == ["01-notes", "01r-research"] and p[2] == BATCH_HUBS:
            hm = BATCH_HUB_FILE.match(seg)              # ORGANIZE 1.14: a batch hub is NNNN-<name>.md, a word name
            if seg == BATCH_HUBS + ".md":
                continue
            if not hm:
                out.append(("names", f"'{seg}': {BATCH_HUBS} holds one hub per batch, named NNNN-<name>.md, and its hub {BATCH_HUBS}.md"))
            elif DATED.search(hm.group(2)) or IDTOK.search(hm.group(2)):
                out.append(("names", f"'{seg}' carries a date or ID after its batch number"))
            continue
        if i == 3 and last and not is_dir and p[:2] == ["01-notes", "01r-research"] and p[2] in RESEARCH_KINDS:
            if not (NOTE_ID.match(stem) and ID_EXT.match(ext)) and seg != p[2] + ".md":    # ORGANIZE 1.12 and 1.15: flat, named by id
                out.append(("names", f"'{seg}': a research kind folder holds files named by their id (<id>.<ext>), and its hub {p[2]}.md"))
            continue
        if i == 2 and last and not is_dir and p[:2] == ["01-notes", TASKS] and ext == "md" and seg != TASKS + ".md":
            if not NOTE_ID.match(stem):                 # ORGANIZE 1.22: one note per task, named by its id
                out.append(("names", f"'{seg}': a task is one note named by its id (<id>.md), and the folder's hub is {TASKS}.md"))
            continue
        if not dir_seg and ext != "md" and ID_EXT.match(ext) and NOTE_ID.match(stem) and p[0] == "01-notes" and i >= 2 and last:
            continue                                # ORGANIZE 1.15: a data, script or drawing file we made is <id>.<ext>, flat beside its note
        if not dir_seg and ext == "md" and p[0] in ("01-notes", "04-resources") and i >= 3 - (p[1] != "01r-research") and last:
            mm = MEETING_ID.match(stem)
            if mm and NOTE_ID.match(mm.group(1)):
                if p[1] == "01m-meetings":
                    continue                            # ORGANIZE 1.11: meeting-<id>
                out.append(("names", f"'{seg}': only a meeting is named meeting-<id>; it belongs in 01m-meetings"))
                continue
            if NOTE_ID.match(stem):
                if p[1] == "01m-meetings":
                    out.append(("names", f"'{seg}': a meeting is named meeting-<id> (ORGANIZE 1.11)"))
                continue                                # ORGANIZE 1.11: a note is named by its bare id
        if i >= 3 and p[:2] == ["01-notes", "01r-research"] and BATCH_DIR.match(p[2]) and \
                (stem == p[2] or stem.startswith(p[2] + "-")):
            stem = stem[len(p[2]):].lstrip("-")       # a batch's notes carry its folder name, number included;
            if not stem:                              # the folder name itself is checked as the folder
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



def folder_faults(d):
    """ORGANIZE 1.15: inside 01-notes, 04-resources and 00-inbox the only folders are the lettered kind folders and
    their sub-kind folders. d is a store-relative folder path (it may not exist yet); returns why it is not allowed."""
    p = parts(d)
    if not p or any(x.startswith(".") for x in p) or p[0] not in FLAT_TOPS or len(p) < 3:
        return []
    if p[0] in ("02-projects", "03-areas"):
        return []                                   # already reported by the names check
    if len(p) == 3 and p[0] == "01-notes" and subkind(p[1], p[2]):
        return []
    if p == ["04-resources", "04h-harness", "04hp-prompts"]:
        return []                                   # ORGANIZE 1.21: the one 04 sub-kind folder
    if (p[0] == "01-notes" or p[:2] == ["04-resources", "04h-harness"]) and len(p) == 3 and nonnote(p[1], p[2]):   # 04h: ORGANIZE 1.21
        return []                                   # ORGANIZE 1.16: 01-notes/<kind>/scripts|data|drawings
    if p[0] == "01-notes" and len(p) == 4 and nonnote(p[2], p[3]) and subkind(p[1], p[2]):
        return []                                   # ORGANIZE 1.16: 01-notes/<kind>/<sub-kind>/scripts|data|drawings
    return ["inside 01-notes, 04-resources and 00-inbox the only folders are the lettered kind folders, "
            "their sub-kind folders, and in 01-notes their scripts/, data/ and drawings/ (ORGANIZE 1.16)"]

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
    # ORGANIZE 1.15: inside 01-notes and 04-resources the only folders are the lettered kind folders and their sub-kind
    # folders; 00-inbox, 02-projects and 03-areas hold no folders below their lettered ones.
    for d in dirs:
        v += [("folders", d + "/", w) for w in folder_faults(d)]
    # two paths that differ only by letter case are one file on macOS and Windows disks, anywhere
    by_low = {}
    for x in files + [d + "/" for d in dirs]:
        by_low.setdefault(x.lower(), []).append(x)
    for group in by_low.values():
        if len(group) > 1:
            for x in group:
                others = ", ".join(g for g in group if g != x)
                v.append(("names", x, f"differs from {others} only by letter case; one of them must be renamed"))
    texts = {}
    for f in files:
        if f.endswith(".md") and not captured(f):
            try:
                texts[f] = open(os.path.join(store, f), encoding="utf-8", errors="replace").read()
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
                rd = folder_note(r, fileset)
                if rd:
                    queue.append(rd)
            elif r in fileset:
                p = parts(r)
                if p[0] in TOPS and (len(p) == ITEM_DEPTH[p[0]] or
                                     (len(p) == ITEM_DEPTH[p[0]] + 1 and is_folder_note(r))):
                    reached_items.add(item_of(r))
                if r.endswith(".md"):
                    queue.append(r)
                else:
                    reached_files.add(r)                # ORGANIZE 1.15: a data, script or drawing file is reached by the note that links it
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
        if captured(f) or f.startswith(".") or "/." in f or is_folder_note(f) or not f.endswith(".md"):
            continue                                # twins are Markdown notes; identical data or script files are records
        fp = os.path.join(store, f)
        try:
            if os.path.getsize(fp) == 0:
                continue
            h = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        except OSError:
            continue
        by_hash.setdefault(h, []).append(f)
    for h, group in by_hash.items():
        if len(group) > 1:
            for f in group:
                others = ", ".join(g for g in group if g != f)
                v.append(("twins", f, f"same bytes as {others}; keep one home and link to it"))
    # maps: every item is linked from an area or project map note
    maps = [f for f in files if f.endswith(".md") and not f.endswith("README.md") and (
            len(parts(f)) == 2 and parts(f)[0] in ("03-areas", "02-projects"))]
    targets = set()
    for m in maps:
        targets.update(edges.get(m, []))
    items = set()
    for f in files:
        p = parts(f)
        if len(p) < 3 or p[0] not in ("01-notes", "04-resources") or f.startswith(".") or "/." in f:
            continue
        if len(p) == 3 and is_folder_note(f):
            continue                                # a lettered folder's hub, not an item
        if p[0] == "01-notes" and (NONNOTE_SEG.match(p[2]) or (len(p) >= 5 and NONNOTE_SEG.match(p[3]))):
            continue                                # ORGANIZE 1.16: a script, data file or drawing is covered by the notes that cite it
        if len(p) >= 4 and p[:2] == ["01-notes", "01r-research"] and p[2] in RESEARCH_KINDS:
            continue                                # ORGANIZE 1.12: a research note is covered by its batch hub (checked below)
        if len(p) >= 4 and p[:3] == ["01-notes", "01r-research", BATCH_HUBS]:
            if len(p) == 4 and not is_folder_note(f):
                items.add("/".join(p[:4]))          # ORGANIZE 1.14: each batch hub is an item, mapped like a batch folder was
            continue
        if len(p) >= 4 and p[:3] == ["04-resources", "04h-harness", "04hp-prompts"]:
            continue                                # ORGANIZE 1.21: captured chat exports, covered by the mapped 04h hub
        if len(p) >= 4 and subkind(p[1], p[2]):     # ORGANIZE 1.10: items of a sub-kind folder sit one deeper
            if len(p) == 4 and is_folder_note(f):
                continue
            items.add("/".join(p[:4]))
            continue
        if p[:2] == ["01-notes", "01d-daily"]:
            continue                                # ORGANIZE 1.9: day logs are mapped by their hub, 01d-daily.md
        items.add("/".join(p[:3]))
    # ORGANIZE 1.13: pages and resources sit flat in their lettered folder. A flat note is covered when a mapped note
    # of the same lettered folder links it (a resource note links its clippings; a page links its notes), and a
    # leftover inner folder (data/, scripts/, drawings/) is covered by the page of the same name.
    flat = lambda f: len(parts(f)) == 3 and parts(f)[0] in ("01-notes", "04-resources")
    for t in sorted(targets):
        if flat(t):
            # ORGANIZE 1.20: a resource note in 04d-documents links its clippings in 04c-clippings
            targets.update(r for r in edges.get(t, []) if (flat(r) or (len(parts(r)) == 4 and parts(r)[:2] == ["04-resources", "04h-harness"])) and (parts(r)[:2] == parts(t)[:2]
                           or parts(r)[0] == parts(t)[0] == "04-resources"))
    for it in sorted(items):
        if it in targets or any(t.startswith(it + "/") for t in targets):
            continue
        if it + ".md" in targets:
            continue
        v.append(("maps", it, "no area or project map links it; link it from 03-areas/<area>.md or 02-projects/<project>.md"))
    for d in dirs:
        p = parts(d)
        if len(p) == 2 and p[0] == "02-projects":
            v.append(("maps", d + "/", f"a project is one map note, 02-projects/{p[1]}.md, with links only; "
                                       "its plans are notes of their kind, such as 01-notes/01h-handbook/ (ORGANIZE 1.8)"))
    v += hubs(store)
    v += map_faults(store)
    v += research_faults(fileset, texts, edges)
    v += task_faults(fileset, texts)
    v += tag_faults(texts)
    if only is not None:
        only = {o.rstrip("/") for o in only}
        v = [x for x in v if x[1].rstrip("/") in only]
    return sorted(set(v))


BATCH_FM = re.compile(r"^batch:[ \t]*(\S+)[ \t]*$", re.M)


def research_faults(fileset, texts, edges):
    """ORGANIZE 1.12: a note in a research kind folder names its batch in front matter, and that batch's hub links it."""
    v = []
    for f in sorted(fileset):
        p = parts(f)
        if len(p) != 4 or p[:2] != ["01-notes", "01r-research"] or p[2] not in RESEARCH_KINDS or not f.endswith(".md"):
            continue
        if p[3] == p[2] + ".md":
            continue                                # the kind folder's own hub
        text = texts.get(f, "")
        fm = text.split("\n---\n", 1)[0] if text.startswith("---\n") else ""
        m = BATCH_FM.search(fm)
        b = m.group(1).strip("\"'") if m else ""
        if not b:
            v.append(("research", f, "front matter has no `batch: NNNN-<name>` (ORGANIZE 1.12)"))
            continue
        hub = f"01-notes/01r-research/{BATCH_HUBS}/{b}.md"
        if not BATCH_DIR.match(b) or hub not in fileset:
            v.append(("research", f, f"`batch: {b}` names no batch hub in {BATCH_HUBS}"))
        elif f not in edges.get(hub, []):
            v.append(("research", f, f"its batch hub {hub} does not link it"))
    return v


def front_matter(text):
    """{key: raw value} of the leading front matter block; empty when there is none."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    out = {}
    for line in text[4:end if end >= 0 else 4].splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):[ \t]*(.*)$", line)
        if m:
            v = m.group(2).strip()
            out[m.group(1)] = v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"" else v
    return out


def task_faults(fileset, texts):
    """ORGANIZE 1.22: each task note carries the same front matter: type, label and state (plus waits-on, owner,
    horizon and source, which are free text and not checked)."""
    v = []
    for f in sorted(fileset):
        p = parts(f)
        if len(p) != 3 or p[:2] != ["01-notes", TASKS] or not f.endswith(".md") or p[2] == TASKS + ".md":
            continue
        fm = front_matter(texts.get(f, ""))
        if fm.get("type") != "task":
            v.append(("tasks", f, "front matter needs `type: task` (ORGANIZE 1.22)"))
        if not TASK_LABEL.match(fm.get("label", "")):
            v.append(("tasks", f, "front matter needs `label: BL-NNNN` (ORGANIZE 1.22)"))
        if fm.get("state") not in TASK_STATES:
            v.append(("tasks", f, f"front matter `state` must be one of {', '.join(TASK_STATES)} (ORGANIZE 1.22)"))
    return v


# ORGANIZE 1.23: kind words a note's tags carry, by the folder it sits in (the longest matching folder wins).
KIND_TAGS = {
    "00-inbox": ["inbox"], "00-inbox/00t-thoughts": ["thought"], "00-inbox/00c-clippings": ["inbox", "clippings"],
    "00-inbox/00e-excalidraw": ["inbox", "drawing"],
    "01-notes": ["note"], "01-notes/01a-atomic": ["note"], "01-notes/01r-research": ["note", "research"],
    "01-notes/01m-meetings": ["meeting"], "01-notes/01h-handbook": ["note", "handbook"],
    "01-notes/01h-handbook/01hr-runbooks": ["note", "runbook"], "01-notes/01s-samples": ["note", "sample"],
    "01-notes/01t-tasks": ["task"], "01-notes/01w-worklogs": ["note", "worklog"],
    "01-notes/01i-incidents": ["note", "incident"],
    "02-projects": ["project"], "03-areas": ["moc"],
    "04-resources": ["resource"], "04-resources/04c-clippings": ["resource", "clippings"],
    "04-resources/04r-repos": ["resource", "repo"], "04-resources/04d-documents": ["resource", "document"],
    "04-resources/04v-video": ["resource", "video"], "04-resources/04l-learning": ["resource", "course"],
    "04-resources/04h-harness": ["resource", "harness"],
}
TAGS_SKIP = ("05-archive/", "99-meta/", "01-notes/01d-daily/")      # kept as it was; the store's own; written by a script
TAGS_LINE = re.compile(r"^tags:[ \t]*\[([^\]\n]*)\]", re.M)
# A body tag as Obsidian reads one: `#` at line start or after white space, then no white space or punctuation.
BODY_TAG = re.compile(r"(?<!\S)#([^\s!\"#$%&'()*+,.:;<=>?@\[\\\]^`{|}~]+)")
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1")
BODY_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def body_tags(text):
    """(line number, tag) for each #tag in the body; front matter, fenced code and code spans are skipped."""
    out, fence, start = [], None, 0
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            start = text.count("\n", 0, end + 4)
    for n, line in enumerate(text.split("\n")[start + 1 if start else 0:], start=start + 2 if start else 1):
        m = BODY_FENCE.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
        elif m:
            fence = m.group(1)
        else:
            for t in BODY_TAG.finditer(CODE_SPAN.sub(lambda c: " " * len(c.group(0)), line)):
                if not t.group(1).isdigit():
                    out.append((n, t.group(1)))
    return out


def tag_faults(texts):
    """ORGANIZE 1.23 and the body-tag rule: tags live in front matter only, and each note's tags carry its kind
    words and its month. Area and topic tags come from each store's own lists, so this check leaves them to the store."""
    v = []
    for f in sorted(texts):
        text = texts[f]
        for n, t in body_tags(text):
            v.append(("tags", f, f"line {n}: body text holds the tag #{t}; tags go in front matter (write the # as &#35;)"))
        if "/" not in f or f.startswith(TAGS_SKIP) or not text.startswith("---\n"):
            continue
        head = text[4:max(text.find("\n---", 4), 4)]
        m = TAGS_LINE.search(head)
        if not m:
            continue                                # no one-line tags list: nothing to compare
        have = {x.strip().strip("\"'") for x in m.group(1).split(",") if x.strip()}
        best = max((k for k in KIND_TAGS if f.startswith(k + "/")), key=len, default=None)
        want = list(KIND_TAGS.get(best, []))
        fm = front_matter(text)
        for src, rx in ((fm.get("created", ""), r"^(\d{4})-(\d{2})-\d{2}"), (fm.get("id", ""), r"^(\d{4})(\d{2})\d{10}$")):
            mm = re.match(rx, src)
            if mm:
                want.append(f"{mm.group(2)}-{mm.group(1)}"); break
        miss = [t for t in want if t not in have]
        if miss:
            v.append(("tags", f, f"tags lack {', '.join(miss)} (kind words of its folder and its month, ORGANIZE 1.23)"))
    return v


def since(store, ref):
    import subprocess, tarfile, tempfile, io
    top = subprocess.run(["git", "-C", store, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    if not top:
        return None
    if subprocess.run(["git", "-C", top, "rev-parse", "--verify", "--quiet", ref + "^{commit}"],
                      capture_output=True).returncode:
        return "bad-ref"
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
    # A name the repo has used before is not new: restores and byte-identical copies
    # paired by -M keep their original names. "Before" means the history of <ref>, plus
    # commits on other refs that HEAD does not contain (files brought back from another
    # branch). Commits reachable from HEAD but not from <ref> are the change under check,
    # so they never count: with plain --all, a newly committed bad name hid itself.
    known = set()
    for rev in ([ref], ["--all", "--not", "HEAD"]):
        hist = subprocess.run(["git", "-C", top, "log", *rev, "--name-only", "--format=", "--no-renames"],
                              capture_output=True, text=True).stdout.split("\n")
        known |= {posixpath.basename(x) for x in hist if x}
    new = [f for f in new if posixpath.basename(f) not in known]
    v = []
    for f in new:
        if f.startswith(prefix):
            rel = f[len(prefix):]
            v += [(c, rel, w) for c, w in name_faults(rel)]
    # If the change adds the store itself, it is not in <ref>: nothing was there before,
    # so every fault in it is new. (git archive fails on a path <ref> does not have.)
    before = []
    if not prefix or subprocess.run(["git", "-C", top, "cat-file", "-e", ref + ":" + prefix.rstrip("/")],
                                    capture_output=True).returncode == 0:
        with tempfile.TemporaryDirectory() as tmp:
            arc = subprocess.run(["git", "-C", top, "archive", "--format=tar", ref, "--", prefix or "."],
                                 capture_output=True)
            if arc.returncode:
                return [("since", ref, "git archive failed: " + arc.stderr.decode(errors="replace").strip()[:200])]
            tf = tarfile.open(fileobj=io.BytesIO(arc.stdout))
            try:
                tf.extractall(tmp, filter="data")
            except TypeError:
                tf.extractall(tmp)
            base = os.path.join(tmp, prefix) if prefix else tmp
            before = check(base) if os.path.isdir(base) else []
    after = check(store)
    for c in ("root", "links", "orphans", "twins", "hubs", "maps", "shape", "research", "folders", "tasks", "tags"):
        nb = sum(1 for x in before if x[0] == c)
        na = [x for x in after if x[0] == c]
        if len(na) > nb:
            v.append((c, "(store)", f"{len(na)} now, {nb} at {ref}; fix the new ones"))
            v += [x for x in na][:20]
    return v


def description(fp):
    try:
        text = open(fp, encoding="utf-8", errors="replace").read(4000)
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
            for x in sorted(os.listdir(d)):
                if os.path.isdir(os.path.join(d, x)):
                    out.append(t + "/" + x)
                    out += [t + "/" + x + "/" + y for y in sorted(os.listdir(os.path.join(d, x)))
                            if subkind(x, y) and not nonnote(x, y) and os.path.isdir(os.path.join(d, x, y))]
    return out


def hub_note(store, hub):
    if not hub:
        return "README.md"
    own = posixpath.join(hub, posixpath.basename(hub) + ".md")
    return own if os.path.exists(os.path.join(store, own)) else posixpath.join(hub, "README.md")


def hub_children(store, hub):
    """Store-relative paths a hub README must link."""
    d = os.path.join(store, hub)
    own = posixpath.basename(hub) + ".md" if hub else "README.md"
    names = sorted(x for x in os.listdir(d) if not x.startswith(".") and x not in ("README.md", own))
    if not hub:
        names = [x for x in names if x in TOPS]
    out = []
    for x in names:
        rel = posixpath.join(hub, x) if hub else x
        out.append(rel)
    return out


def hub_lines(store, hub):
    """(resolved target, words besides the links) for every link line of the hub README."""
    rel = hub_note(store, hub)
    try:
        text = open(os.path.join(store, rel), encoding="utf-8", errors="replace").read()
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
        rel = hub_note(store, h)
        got = hub_lines(store, h)
        if got is None:
            v.append(("hubs", rel, "hub has no note"))
            got = []
        for c in hub_children(store, h):
            hits = [n for r, n in got if r == c or r.startswith(c + "/")]
            if not hits:
                v.append(("hubs", rel, f"does not link its child '{posixpath.basename(c)}'"))
                fp = os.path.join(store, c)
                fn = folder_note(c, {posixpath.join(c, x) for x in os.listdir(fp)}) if os.path.isdir(fp) else None
                desc = description(os.path.join(store, fn) if fn else fp)
                x = posixpath.basename(c)
                lines.append(f"{rel}: - [{x}]({x}{'/' if os.path.isdir(fp) else ''}): {desc or '<description>'}")
            elif max(hits) < 2:
                v.append(("hubs", rel, f"the line linking '{posixpath.basename(c)}' has no description"))
    if suggest:
        print("\n".join(lines) or "every hub links all its children")
    return v


# ---- map shape (ORGANIZE 1.7): one template per map kind, link sections written by this file ----
MAP_START = "<!-- map: start (written by org_check.py --maps-write) -->"
MAP_END = "<!-- map: end -->"
TAG_START, TAG_END = "<!-- tag-map: start (written by tag_maps.py) -->", "<!-- tag-map: end -->"
TAG_HEAD = "## Items tagged with this area"
NOT_WRITTEN = "_Not written yet._"
# Generated link sections, in this order: (heading, store-path prefix of the link target).
MAP_KINDS = [("Projects", "02-projects/"), ("Areas", "03-areas/"),
             ("Research batches", "01-notes/01r-research/"), ("Runbooks", "01-notes/01h-handbook/01hr-runbooks/"),
             ("Handbook pages", "01-notes/01h-handbook/"), ("Tasks", "01-notes/01t-tasks/"), ("Incidents", "01-notes/01i-incidents/"),
             ("Worklogs", "01-notes/01w-worklogs/"), ("Meetings", "01-notes/01m-meetings/"),
             ("Atomic notes", "01-notes/01a-atomic/"), ("Samples", "01-notes/01s-samples/"),
             ("Day logs", "01-notes/01d-daily/"), ("Resources", "04-resources/"), ("Inbox", "00-inbox/"),
             ("Archive", "05-archive/"), ("How this store works", "99-meta/")]
# Old link-section headings that the generated block replaces (organize-moves/reorg2.py, clip_resources.py).
OLD_LINK_HEADS = {"research batches", "investigations and samples", "resources", "resources: sources of batches",
                  "living pages", "plans", "elsewhere"} | {k.lower() for k, _ in MAP_KINDS}
# The marker keeps the name of the store tool that first wrote it, so stores that use either tool read the same maps.
MAP_FOOTER = ("_Written by `check_knowledge_store.py --maps-write` from the link lines in this map. To add a link, put a "
              "line `- [Name](path): reason` anywhere in this block and run "
              "`check_knowledge_store.py <store> --maps-write`. CI fails when a map is not in this shape._")
LIST_LINK = re.compile(r"^(\s*)[-*] \[([^\]]+)\]\(\s*<?([^)\s>]+)>?\)(.*)$")


def map_kind(rel):
    p = parts(rel)
    if len(p) == 2 and rel.endswith(".md") and p[0] == "03-areas" and p[1] != "03-areas.md":
        return "area"
    if len(p) == 2 and rel.endswith(".md") and p[0] == "02-projects" and p[1] != "02-projects.md":
        return "project"
    return None


def map_template(store, kind):
    """(hand headings in order, catch-all heading) from 99-meta/templates/<kind>-map.md, or None."""
    fp = os.path.join(store, "99-meta", "templates", kind + "-map.md")
    try:
        text = open(fp, encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r"^```markdown\n(.*?)^```", text, re.S | re.M)
    body = m.group(1) if m else ""
    hand = body.split(MAP_START)[0]
    heads = [x[3:].strip() for x in hand.splitlines() if x.startswith("## ")]
    catch = re.search(r"^Catch-all section: (.+)$", text, re.M)
    if not heads:
        return None
    return heads, (catch.group(1).strip() if catch else heads[0])


def map_render(store, rel):
    """The map as --maps-write writes it, or None when it is not a map or has no template."""
    kind = map_kind(rel)
    t = kind and map_template(store, kind)
    if not t:
        return None
    heads, catch = t
    text = open(os.path.join(store, rel), encoding="utf-8").read()
    front, body = "", text
    if text.startswith("---\n") and "\n---\n" in text[4:]:
        i = text.index("\n---\n", 4) + 5
        front, body = text[:i], text[i:]
    tag = ""
    if TAG_START in body and TAG_END in body:
        a, b = body.index(TAG_START), body.index(TAG_END) + len(TAG_END)
        tag, body = body[a:b], body[:a] + body[b:]
    block = ""
    if MAP_START in body and MAP_END in body:
        a, b = body.index(MAP_START), body.index(MAP_END) + len(MAP_END)
        block, body = body[a:b], body[:a] + body[b:]
    # Split the rest into the header (title, Up, bold summary) and sections.
    header, pre, secs, cur = [], [], [], None
    for line in body.splitlines():
        if line.startswith("## "):
            cur = [line[3:].strip(), []]
            secs.append(cur)
        elif cur is not None:
            cur[1].append(line)
        elif not header and not line.strip():
            continue
        elif line.startswith("# ") and not header:
            header.append(line)
        elif header and len(pre) == 0 and (line.startswith("Up:") or (line.startswith("**") and line.rstrip().endswith("**"))):
            header.append(line)
        elif header and not line.strip() and not pre:
            continue
        else:
            pre.append(line)
    # Link entries: first from the generated block, then from list lines anywhere else.
    entries, seen = [], set()
    parent_of = {}                                  # an indented sub-link stays under its parent link
    def take(lines):
        last_top = None
        for line in lines:
            m = LIST_LINK.match(line)
            if not m:
                continue
            label, target, rest = m.group(2), m.group(3), m.group(4)
            res = resolve(rel, target)
            if not res or res == rel or not os.path.exists(os.path.join(store, res)):
                continue
            frag = target[len(target.split("#", 1)[0]):]
            key = (res, frag)
            if key in seen:
                continue
            seen.add(key)
            if m.group(1) and last_top:
                parent_of[key] = last_top
            elif not m.group(1):
                last_top = res
            reason = re.sub(r"^\s*(?::|-|–|—)\s*", "", rest).strip()
            entries.append((res, frag, label, reason))
    take(block.splitlines())
    for name, lines in secs:
        if name == TAG_HEAD.lstrip("# "):
            continue
        take(lines)
    take(pre)
    # Hand sections in template order; unknown headings move under the catch-all as ###.
    by_head = {h: [] for h in heads}
    extra = []
    for name, lines in secs:
        if name == TAG_HEAD[3:]:
            continue
        if name in by_head:
            by_head[name] += lines
        elif name.lower() in OLD_LINK_HEADS:
            keep = [x for x in lines if x.strip() and not LIST_LINK.match(x) and not x.startswith("_Agents keep this map current")
                    and not x.startswith("_Written by")]
            if keep:
                extra += [""] + keep
        else:
            extra += ["", "### " + name] + [("#" + x if x.startswith("###") else x) for x in lines]
    by_head[heads[0]] = pre + by_head[heads[0]]
    by_head[catch] = by_head[catch] + extra
    out = []
    for h in header:
        out += [h, ""]
    out = out[:-1]
    for h in heads:
        lines = by_head[h]
        while lines and not lines[0].strip():
            lines = lines[1:]
        while lines and not lines[-1].strip():
            lines = lines[:-1]
        out += ["", "## " + h, ""] + (lines or [NOT_WRITTEN])
    # The generated block.
    def section(res):
        for head, pre_ in MAP_KINDS:
            if res.startswith(pre_):
                return head
        return "How this store works"
    out += ["", MAP_START, ""]
    d = posixpath.dirname(rel)
    for head, _ in MAP_KINDS:
        rows = [e for e in entries if section(parent_of.get((e[0], e[1]), e[0])) == head]    # a sub-link stays in its parent's section
        if not rows:
            continue
        items = {}
        in_map = {e[0] for e in rows}

        def gkey(res, frag=""):
            """ORGANIZE 1.14: a research note under a kind folder is a child of its batch hub when the map links the hub;
            a hub is its own group; other links group by their item. Indented sub-links are kept, not flattened."""
            if (res, frag) in parent_of and parent_of[(res, frag)] in in_map and parent_of[(res, frag)] != res:
                return gkey(parent_of[(res, frag)])
            q = parts(res)
            if len(q) == 4 and q[:3] == ["01-notes", "01r-research", BATCH_HUBS]:
                return res
            if len(q) == 4 and q[:2] == ["01-notes", "01r-research"] and q[2] in RESEARCH_KINDS and res.endswith(".md"):
                try:
                    text = open(os.path.join(store, res), encoding="utf-8", errors="replace").read()
                except OSError:
                    text = ""
                fmb = text.split("\n---\n", 1)[0] if text.startswith("---\n") else ""
                mb = BATCH_FM.search(fmb)
                hub = f"01-notes/01r-research/{BATCH_HUBS}/{mb.group(1).strip(chr(34) + chr(39))}.md" if mb else ""
                if hub in in_map:
                    return hub
            return item_of(res)
        for e in rows:
            items.setdefault(gkey(e[0], e[1]), []).append(e)
        out += ["## " + head, ""]
        for it in sorted(items):
            grp = sorted(items[it], key=lambda e: (not (e[0] == it or is_folder_note(e[0]) or e[0] == it + ".md"), e[0], e[1]))
            top = grp[0][0] == it or is_folder_note(grp[0][0]) or grp[0][0] == it + ".md" or len(grp) == 1
            for i, (res, frag, label, reason) in enumerate(grp):
                why = reason or description(os.path.join(store, res)) or "no description yet"
                ind = "  " if (top and i > 0) else ""
                out.append(f"{ind}- [{label}]({posixpath.relpath(res, d)}{frag}): {why}")
        out.append("")
    footer = next((x for x in block.splitlines() if x.startswith("_Written by ")), MAP_FOOTER)   # keep the store's own
    out += [footer, "", MAP_END]
    if tag:
        out += ["", TAG_HEAD, "", tag]
    lines = front.rstrip("\n").split("\n") + [""] if front else []
    return "\n".join(lines + out).rstrip("\n") + "\n"


def map_faults(store):
    v = []
    for f in sorted(glob_maps(store)):
        want = map_render(store, f)
        if want is not None and want != open(os.path.join(store, f), encoding="utf-8").read():
            v.append(("shape", f, "this map is not in its template's shape (99-meta/templates/); "
                                  "run check_knowledge_store.py <store> --maps-write"))
    return v


def glob_maps(store):
    out = []
    for top in ("02-projects", "03-areas"):
        d = os.path.join(store, top)
        if os.path.isdir(d):
            out += [top + "/" + x for x in os.listdir(d) if map_kind(top + "/" + x)]
    return out


def maps_write(store):
    n = 0
    for f in sorted(glob_maps(store)):
        want = map_render(store, f)
        fp = os.path.join(store, f)
        if want is not None and want != open(fp, encoding="utf-8").read():
            open(fp, "w", encoding="utf-8").write(want)
            print("wrote", f); n += 1
    print(f"maps_write: {n} map(s) rewritten", file=sys.stderr)
    return 0


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
        d = rel if a[2].endswith("/") else posixpath.dirname(rel)
        v += [("folders", rel, w) for w in (folder_faults(d) if d else [])]
    elif len(a) >= 2 and a[1] == "--changed":
        v = check(store, a[2:])
    elif len(a) == 2 and a[1] == "--maps-write":
        return maps_write(store)
    elif len(a) == 2 and a[1] == "--hubs":
        hubs(store, suggest=True)
        return 0
    elif len(a) == 3 and a[1] == "--since":
        v = since(store, a[2])
        if v is None:
            print("not a git repo"); return 2
        if v == "bad-ref":
            print(f"'{a[2]}' is not a commit in this repo"); return 2
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

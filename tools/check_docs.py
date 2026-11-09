#!/usr/bin/env python3
"""Checks the documentation against itself and against the reference table list.

Run: python3 tools/check_docs.py    (stdlib only; no MATLAB, no data needed)

What it catches - each of these was a real defect that shipped:

1. a link to a file that does not exist (the site build only checks rendered html);
2. an output file name that the pipeline does not produce, e.g. the
   05_all_05_all_timing_check.csv class of typo, or a name from two renames ago;
3. a column count in the prose that disagrees with TABLE_LIST,
   e.g. "05_all_trials_wide.csv (14 columns)" drifting away from 14;
4. a guide page that is not in GUIDES, so it never reaches the site.

Exit code 1 on any finding, so the Pages workflow can gate on it.
"""
import ast
import importlib.util
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
DOCS = REPO / "docs"

problems = []


def fail(where, msg):
    problems.append((str(where.relative_to(REPO)), msg))


# --------------------------------------------------------------------------- reference
def load_build_readme():
    spec = importlib.util.spec_from_file_location("br", HERE / "build_readme.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


big = load_build_readme()


def load_guides():
    """Read GUIDES out of build_site.py without importing it (importing builds the site)."""
    tree = ast.parse((HERE / "build_site.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "GUIDES" for t in node.targets):
            return [(n, en, zh) for n, en, zh, _titles in ast.literal_eval(node.value)]
    raise SystemExit("GUIDES not found in tools/build_site.py")


GUIDES = load_guides()


def normalise(name):
    """05_<sub>_markers[_5step].csv -> the two names it stands for; keeps <...> slots."""
    name = name.strip().strip("`")
    name = name.split("/")[-1]
    name = name.rstrip(".,;")
    m = re.fullmatch(r"(.*)\[([^\]]*)\](.*)", name)
    if not m:
        return {name}
    opts = [""] + m.group(2).split("|")          # "[_5step]" means "with or without"
    return {m.group(1) + opt + m.group(3) for opt in opts}


# canonical (name -> declared column count), from TABLE_LIST
CANON = {}
for _label, path, _freq, ncols, _who in big.TABLE_LIST:
    for piece in path.split(", "):
        for nm in normalise(piece):
            CANON[nm] = ncols

# names that are real but are not one row of TABLE_LIST
EXTRA = {
    "05_all_markers.csv": 18,
    "05_all_markers_5step.csv": 18,
}

# --------------------------------------------------------------------------- 1. links
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
for md in sorted(list(DOCS.rglob("*.md")) + [REPO / "README.md"]):
    text = md.read_text(encoding="utf-8")
    for href in LINK.findall(text):
        href = href.strip()
        if not href or href.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = (md.parent / href.split("#")[0]).resolve()
        if not target.exists():
            fail(md, f"link to a missing file: {href}")

# --------------------------------------------------------------------------- 2./3. names
NAME = re.compile(r"\b\d{2}_[A-Za-z0-9_<>\[\]]*\.csv")
COUNT = re.compile(r"(\d{1,2})\s*(?:columns|列)")
DOUBLED = re.compile(r"\b(\d{2})_all_\1_all_")
# The event table was renamed from <sub>_event_table.csv to 05_<sub>_markers.csv and
# the old name survived in comments and in a diagram. No file is called *_event_table*,
# so any occurrence is stale by definition.
LEGACY = re.compile(r"[A-Za-z0-9_<>*]*_event_table(?:_5step)?\.csv")

SOURCES = sorted(list(DOCS.rglob("*.md")) + [REPO / "README.md"] + list((REPO / "code").rglob("*.m")))


def read(path):
    """Upstream .m files are not all UTF-8; we only look at names, so be tolerant."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


for md in SOURCES:
    text = read(md)
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in DOUBLED.finditer(line):
            fail(md, f"line {lineno}: doubled prefix {m.group(0)} - the pipeline writes one prefix")
        for m in LEGACY.finditer(line):
            fail(md, f"line {lineno}: {m.group(0)} does not exist - the marker table is "
                     f"05_<sub>_markers.csv / 05_all_markers.csv")
        names = NAME.findall(line)
        for raw in names:
            nm = raw
            if nm in CANON or nm in EXTRA:
                continue
            if any(nm in normalise(k) for k in CANON):
                continue
            if re.fullmatch(r"05_sub\d+_markers(_5step)?\.csv", nm):
                continue                      # a concrete example of the <sub> slot
            fail(md, f"line {lineno}: {nm} is not an output any script in this repository writes "
                     f"(see TABLE_LIST in tools/build_readme.py)")
        counts = COUNT.findall(line)
        if len(names) == 1 and len(counts) == 1:
            nm, n = names[0], int(counts[0])
            want = CANON.get(nm, EXTRA.get(nm))
            if want is not None and want != n:
                fail(md, f"line {lineno}: {nm} is declared as {n} columns, TABLE_LIST says {want}")

# --------------------------------------------------------------------------- 4. the generated reference
# code/README.md is generated from tools/build_readme.py. It drifted twice (stale file names
# and a paragraph that existed only on one side), so compare the two instead of trusting them.
if hasattr(big, "build_text"):
    try:
        generated = big.build_text()
    except Exception as exc:                      # a broken generator is a finding of its own
        fail(REPO / "tools" / "build_readme.py", f"build_text() failed: {exc}")
    else:
        on_disk = REPO / "code" / "README.md"
        if not on_disk.is_file():
            fail(on_disk, "missing: run `python3 tools/build_readme.py`")
        elif on_disk.read_text(encoding="utf-8") != generated:
            fail(on_disk, "is stale: it is generated, run `python3 tools/build_readme.py`")

# --------------------------------------------------------------------------- 5. page set
listed = set()
for _n, en, zh in GUIDES:
    listed.update({f"docs/{en}", f"docs/{zh}"})
    for rel in (en, zh):
        if not (DOCS / rel).exists():
            fail(DOCS / rel, "listed in GUIDES but the file does not exist")
for md in sorted(DOCS.rglob("*.md")):
    rel = str(md.relative_to(REPO))
    if rel == "docs/README.md":
        continue
    if rel not in listed:
        fail(md, "page is not in GUIDES (tools/build_site.py), so it never reaches the site")

# --------------------------------------------------------------------------- report
if problems:
    for where, msg in problems:
        print(f"{where}: {msg}")
    print(f"\n{len(problems)} problem(s).")
    sys.exit(1)
print(f"docs ok: {len(listed)} guide pages, {len(CANON) + len(EXTRA)} output names, "
      f"{len(SOURCES)} files scanned, links resolve.")

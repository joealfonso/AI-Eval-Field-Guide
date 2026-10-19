#!/usr/bin/env python3
"""Single source of truth for the Bibliography and for every source count on the site.

The bibliography is not hand-maintained. It is computed from:
  - data/laws.json                      sources listed on the 26 pattern pages
  - the manuscript's reference lists    sources cited in the Overview, Being Pragmatic,
                                        Playbook and Glossary (their "### References" lists)
  - data/sameWork.json                  versions of one study listed separately (counted once)
  - data/sourceKinds.json               unlabeled entries that are not ordinary peer-reviewed papers

Definitions used everywhere on the site:
  citations   one source line on one pattern page (the same work cited on three pages is three citations)
  works       distinct pieces of research, after merging versions of the same study (sameWork.json)

Python 3 standard library only. Run `python3 build/bibliography.py --write-manuscript` to refresh the
Bibliography section of the manuscript (content/source/ai-evaluation-field-guide-full.md) from the data,
and `python3 build/bibliography.py` to print the counts.
"""
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import import_manuscript as im  # noqa: E402

ROOT = im.ROOT
SRC = im.SRC

# Reference lists outside the patterns: (name shown in "Cited in", first heading, heading that ends the region).
# The order here is the order the names appear after the pattern names in "Cited in".
SECTIONS = [
    ("Being Pragmatic", "## Being Pragmatic", "## Playbook"),
    ("Playbook", "## Playbook", "## Glossary"),
    ("Glossary", "## Glossary", "## Bibliography"),
    ("Overview", "## AI Evaluation, an Overview", "## The Patterns"),
]


def _load(name):
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _region(lines, start, end):
    a = next(i for i, l in enumerate(lines) if l.strip() == start)
    b = next((i for i, l in enumerate(lines) if i > a and l.strip() == end), len(lines))
    return lines[a + 1 : b]


def section_references(lines, start, end):
    """Sources in the '### References' list of one manuscript section."""
    reg = _region(lines, start, end)
    try:
        a = next(i for i, l in enumerate(reg) if l.strip() == "### References")
    except StopIteration:
        return []
    out = []
    for l in reg[a + 1 :]:
        if l.startswith("#"):
            break
        if l.startswith("- "):
            out.append(im.parse_source(l))
    return out


def work_key(s, alias_to_primary):
    """Identity of a work: its link when it has one, otherwise title and year."""
    if s["url"] and s["url"] in alias_to_primary:
        return alias_to_primary[s["url"]]
    return norm(s["title"]) + s["year"]


def short_authors(a):
    return a.split(",")[0].strip()


def build_model(laws=None):
    laws = laws if laws is not None else json.loads((ROOT / "data/laws.json").read_text(encoding="utf-8"))
    same = _load("sameWork.json").get("works", [])
    kinds = _load("sourceKinds.json").get("works", [])
    alias_to_primary = {}
    for w in same:
        for a in w["alsoCirculatedAs"]:
            alias_to_primary[a["url"]] = norm_url_key(w["primaryUrl"])
        alias_to_primary[w["primaryUrl"]] = norm_url_key(w["primaryUrl"])
    kind_by_title = {norm(k["title"]): k for k in kinds}

    lines = im.SRC.read_text(encoding="utf-8").split("\n")
    entries = collections.OrderedDict()
    mismatches = []

    def add(src, where, is_pattern):
        k = work_key(src, alias_to_primary)
        primary_url = next((w["primaryUrl"] for w in same if norm_url_key(w["primaryUrl"]) == k), None)
        alias = next((a for w in same for a in w["alsoCirculatedAs"] if a["url"] == src["url"]), None)
        e = entries.get(k)
        if e is None:
            e = entries[k] = {"key": k, "primary": None, "alsoAs": [], "patterns": [], "pages": [], "variants": []}
        if alias is not None:
            if not any(x["url"] == src["url"] for x in e["alsoAs"]):
                e["alsoAs"].append(dict(src, note=alias.get("note", "")))
        else:
            if e["primary"] is None:
                e["primary"] = src
            else:
                sig = lambda s: (norm(s["authors"]), s["year"], norm(s["venue"]), s["label"], s["url"])
                if sig(src) != sig(e["primary"]):
                    mismatches.append((where, src, e["primary"]))
        if is_pattern:
            if where not in e["patterns"]:
                e["patterns"].append(where)
        elif where not in e["pages"]:
            e["pages"].append(where)

    for law in laws:
        for s in law["sources"]:
            add(s, law["slug"], True)
    for name, a, b in SECTIONS:
        for s in section_references(lines, a, b):
            add(s, name, False)

    out = []
    for k, e in entries.items():
        if e["primary"] is None:  # only an alias was cited: promote it so the work is not lost
            e["primary"] = e["alsoAs"].pop(0)
        p = e["primary"]
        kind = None if p["label"] else kind_by_title.get(norm(p["title"]))
        e["kind"] = kind
        e["pages"].sort(key=lambda n: [s[0] for s in SECTIONS].index(n))
        out.append(e)
    out.sort(key=lambda e: (e["primary"]["authors"].lower(), e["primary"]["year"]))
    return {"entries": out, "mismatches": mismatches, "laws": laws}


def norm_url_key(u):
    return "url:" + u


def counts(model):
    """Every source count the site states, computed once."""
    laws = model["laws"]
    entries = model["entries"]
    citations = sum(len(l["sources"]) for l in laws)
    on_patterns = [e for e in entries if e["patterns"]]
    by_type = collections.Counter(e["primary"]["label"] or "peer" for e in entries)
    flagged = [e for e in entries if e["kind"]]
    return {
        "citations": citations,
        "works_on_patterns": len(on_patterns),
        "works_total": len(entries),
        "only_elsewhere": len(entries) - len(on_patterns),
        "by_type": by_type,
        "merged": [e for e in entries if e["alsoAs"]],
        "flagged": flagged,
    }


LABEL_PLURAL = collections.OrderedDict([
    ("Preprint", ("preprint", "preprints")),
    ("Report", ("report", "reports")),
    ("Regulation", ("regulation", "regulations")),
    ("Working paper", ("working paper", "working papers")),
    ("Book", ("book", "books")),
])


def type_breakdown_text(c):
    """'N are peer-reviewed or classic, N are preprints, ...' computed from the data. Zero counts are skipped."""
    parts = []
    t = c["by_type"]
    if t["peer"]:
        parts.append("%d appeared in a peer-reviewed venue or are long-established classics" % t["peer"])
    for label, (one, many) in LABEL_PLURAL.items():
        if t[label]:
            parts.append("%d %s %s" % (t[label], "is a" if t[label] == 1 else "are", one if t[label] == 1 else many))
    for label in sorted(set(t) - {"peer"} - set(LABEL_PLURAL)):
        parts.append("%d labeled %s" % (t[label], label.lower()))
    return parts


def dedupe_note(e):
    """Plain-language description of a work that has more than one listed version."""
    p = e["primary"]
    alt = e["alsoAs"][0]
    kind = (alt["label"] or "earlier version").lower()
    return "the %s %s and the %s published version of %s et al." % (alt["year"], kind, p["year"], short_authors(p["authors"]))


def kinds_sentence(c):
    """Names the unlabeled entries that are not ordinary peer-reviewed papers, grouped by kind. Empty if none."""
    groups = collections.OrderedDict()
    for e in c["flagged"]:
        groups.setdefault(e["kind"]["group"], []).append(e["kind"]["short"])
    return "; ".join("%s (%s)" % (g, "; ".join(items)) for g, items in groups.items())


def intro_text(model):
    c = counts(model)
    flagged = kinds_sentence(c)
    s = ("%d works are cited across the guide: %d on the pattern pages, and %d more that appear only in the Overview, Being Pragmatic, Playbook or Glossary. "
         "A work counts once however many pages cite it, and two versions of one study count as one. "
         "Preprints, reports, regulations, working papers and books are labeled. Every other entry appeared in a peer-reviewed venue or is a long-established classic"
         % (c["works_total"], c["works_on_patterns"], c["only_elsewhere"]))
    if flagged:
        s += ", except these, which carry their own tag: %s" % flagged
    return s + "."


def entry_line(e):
    """One entry in the manuscript's Bibliography format (markdown)."""
    p = e["primary"]
    esc_star = lambda t: t.replace("*", "\\*")
    head = "%s (%s). " % (esc_star(p["authors"]), p["year"])
    if p["url"]:
        url = p["url"].replace("(", "\\(").replace(")", "\\)")
        body = "[%s](%s). %s" % (esc_star(p["title"]), url, esc_star(p["venue"]))
    else:
        body = "%s. %s" % (esc_star(p["title"]), esc_star(p["venue"]))
    tag = p["label"] or (e["kind"]["tag"] if e["kind"] else None)
    if tag:
        body += (". " if not body.endswith(".") else " ") + "*(%s)*" % tag
    elif not body.endswith("."):
        body += "."
    return head + body


def write_manuscript(model):
    lines = SRC.read_text(encoding="utf-8").split("\n")
    a = next(i for i, l in enumerate(lines) if l.strip() == "## Bibliography")
    names = {l["slug"]: l["name"] for l in model["laws"]}
    body = ["", intro_text(model), ""]
    for e in model["entries"]:
        body.append("- " + entry_line(e) + "  ")
        body.append("  Cited in: " + ", ".join([names[s] for s in e["patterns"]] + e["pages"]) + "  ")
        for alt in e["alsoAs"]:
            body.append("  Also circulated as: %s (%s), %s.  " % (alt["title"], alt["year"], alt["venue"]))
    lines = lines[: a + 1] + body + ["", "&nbsp;", ""]
    SRC.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    m = build_model()
    c = counts(m)
    print("citations:", c["citations"], "| works on patterns:", c["works_on_patterns"], "| works total:", c["works_total"], "| cited only elsewhere:", c["only_elsewhere"])
    print("by type:", dict(c["by_type"]))
    print("merged:", [e["primary"]["authors"][:20] + " " + e["primary"]["year"] for e in c["merged"]], "| tagged:", [e["kind"]["tag"] for e in c["flagged"]])
    for where, s, p in m["mismatches"]:
        print("METADATA MISMATCH between occurrences of one work:", where, "|", s["authors"][:30], s["year"], s["venue"][:50], s["label"], "vs", p["venue"][:50], p["label"])
    if "--write-manuscript" in sys.argv:
        write_manuscript(m)
        print("manuscript Bibliography section rewritten")

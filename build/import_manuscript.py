#!/usr/bin/env python3
"""Parse content/source/laws-of-ai-evaluation-full.md into data/laws.json and data/glossary.json.

Re-run after editing the manuscript, then run build.py. Python 3 standard library only.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "content/source/laws-of-ai-evaluation-full.md"

CATEGORIES = {
    "What you're measuring": "I",
    "The test itself": "II",
    "Running the eval": "III",
    "Reading the results": "IV",
    "Beyond the benchmark": "V",
}

# Sources the manuscript lists without a link; title and venue are split by hand
# because "Title. Venue." cannot be separated reliably.
UNLINKED = {
    ("Goodhart", "1975"): ("Problems of monetary management: The U.K. experience", "Papers in Monetary Economics, Vol. 1. Reserve Bank of Australia"),
    ("Strathern", "1997"): ("'Improving ratings': Audit in the British university system", "European Review, 5(3), 305-321"),
    ("Roelofs", "2019"): ("A meta-analysis of overfitting in machine learning", "Advances in Neural Information Processing Systems (NeurIPS 2019)"),
    ("Moravec", "1988"): ("Mind children: The future of robot and human intelligence", "Harvard University Press"),
}


def unescape(s):
    """Resolve markdown escapes, keeping \\* and \\_ so they are not read as emphasis."""
    return re.sub(r"\\([^A-Za-z0-9\s*_])", r"\1", s)


def clean(s):
    return unescape(s.strip()).replace("\u00a0", " ")


def slugify(name):
    s = name.lower().replace("'", "").replace("\u2019", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def blocks(lines):
    """Split a section into paragraphs and bullet items."""
    paras, items, cur = [], [], []
    for ln in lines:
        if ln.startswith("- "):
            if cur:
                paras.append(" ".join(cur))
                cur = []
            items.append(ln[2:].rstrip())
        elif ln.strip() == "":
            if cur:
                paras.append(" ".join(cur))
                cur = []
        elif items and not cur and ln.startswith("  "):
            items[-1] += " " + ln.strip()
        else:
            cur.append(ln.strip())
    if cur:
        paras.append(" ".join(cur))
    return [clean(p) for p in paras], [clean(i) for i in items]


def parse_source(line):
    raw = line[2:].strip()
    label = None
    m = re.search(r"\s*\*\((Preprint|Report|Working paper|Book)\)\*\s*$", raw)
    if m:
        label = m.group(1)
        raw = raw[: m.start()]
    m = re.match(r"^(?P<authors>.+?) \((?P<year>\d{4})\)\.\s+(?P<rest>.+)$", raw)
    if not m:
        sys.exit("Unparsed source line: " + line)
    authors, year, rest = clean(m["authors"]), m["year"], m["rest"]
    lm = re.match(r"^\[(?P<title>(?:\\.|[^\]\\])*)\]\((?P<url>(?:\\.|[^)\\])*)\)\.?\s*(?P<venue>.*)$", rest)
    if lm:
        title, url, venue = clean(lm["title"]), unescape(lm["url"]), clean(lm["venue"]).rstrip(".")
    else:
        key = (authors.split(",")[0], year)
        if key not in UNLINKED:
            sys.exit("Unlinked source needs an UNLINKED override: " + line)
        title, venue = UNLINKED[key]
        url = None
    return {"authors": authors, "year": year, "title": title, "venue": venue, "url": url, "label": label}


def parse_laws(lines):
    laws, cat, law, section = [], None, None, None
    buf = {}

    def flush_section():
        if law is not None and section is not None:
            law["_raw"][section] = buf.get("lines", [])

    for ln in lines:
        if ln.startswith("### "):
            flush_section()
            section = None
            cat = CATEGORIES[clean(ln[4:])]
            law = None
        elif ln.startswith("#### "):
            flush_section()
            section = None
            name = clean(ln[5:])
            law = {"no": "%02d" % (len(laws) + 1), "slug": slugify(name), "name": name, "category": cat, "_raw": {}}
            laws.append(law)
            buf = {"lines": []}
        elif ln.startswith("##### "):
            flush_section()
            section = clean(ln[6:])
            buf = {"lines": []}
        elif law is not None:
            if section is None and ln.startswith("> "):
                law["aphorism"] = clean(ln[2:])
            elif section is not None:
                buf["lines"].append(ln)
    flush_section()

    for law in laws:
        raw = law.pop("_raw")
        law["takeaways"] = blocks(raw["Takeaways"])[1]
        law["whatItMeans"] = blocks(raw["What it means"])[0]
        ev = []
        for item in blocks(raw["The evidence"])[1]:
            m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", item)
            ev.append({"lead": m[1], "text": m[2]} if m else {"lead": "", "text": item})
        law["evidence"] = ev
        law["useIt"] = blocks(raw["Use it"])[1]
        law["origins"] = blocks(raw["Origins"])[0]
        law["sources"] = [parse_source(i) for i in raw["Sources"] if i.startswith("- ")]
    return laws


def parse_glossary(lines):
    out = []
    for ln in lines:
        m = re.match(r"^\*\*(.+?)\.\*\*\s+(.*)$", ln)
        if not m:
            continue
        term, body = clean(m[1]), clean(m[2])
        see = re.findall(r"\*([^*]+)\*", body[body.rfind("See ") :]) if "See *" in body else []
        body = re.sub(r"\s*See \*.*$", "", body)
        out.append({"term": term, "definition": body, "see": see})
    return out


def main():
    text = SRC.read_text(encoding="utf-8")
    lines = text.split("\n")

    def region(start, end):
        a = next(i for i, l in enumerate(lines) if l.strip() == start)
        b = next(i for i, l in enumerate(lines) if i > a and l.strip() == end)
        return lines[a + 1 : b]

    laws = parse_laws(region("## The Laws", "## Being Pragmatic"))
    gloss_lines = region("## Glossary", "### References")
    glossary = parse_glossary(gloss_lines)

    (ROOT / "data/laws.json").write_text(json.dumps(laws, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "data/glossary.json").write_text(json.dumps(glossary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {}
    for law in laws:
        counts[law["category"]] = counts.get(law["category"], 0) + 1
    print("laws:", len(laws), counts, "| sources:", sum(len(l["sources"]) for l in laws), "| glossary terms:", len(glossary))


if __name__ == "__main__":
    main()

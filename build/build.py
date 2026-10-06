#!/usr/bin/env python3
"""Generate the Laws of AI Evaluation static pages.

Reads data/*.json and content/source/*, writes HTML into the site folder plus
js/data.js, js/search-index.js and feed.xml. Python 3 standard library only.

    python3 build/import_manuscript.py   # only after editing the manuscript
    python3 build/build.py
"""
import datetime
import hashlib
import html
import json
import pathlib
import re
import collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "content/source"


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


SITE = load("site.json")
LAWS = load("laws.json")
EDIT = load("editorial.json")
GLOSS = load("glossary.json")
CHANGELOG = load("changelog.json")["entries"]

CATS = [
    {"id": "I", "name": "What you're measuring", "short": "Measuring", "n": 1},
    {"id": "II", "name": "The test itself", "short": "The test", "n": 2},
    {"id": "III", "name": "Running the eval", "short": "Running", "n": 3},
    {"id": "IV", "name": "Reading the results", "short": "Results", "n": 4},
    {"id": "V", "name": "Beyond the benchmark", "short": "Beyond", "n": 5},
]
for _c in CATS:
    _c["thread"] = EDIT["categories"][_c["id"]]["thread"]
CAT = {c["id"]: c for c in CATS}
NAV = [
    ("Laws", "index.html", "laws"),
    ("Claim checker", "claim-checker.html", "claim"),
    ("Design Rubric", "design-rubric.html", "rubric"),
    ("Readiness Review", "readiness-review.html", "review"),
    ("Changelog", "changelog.html", "changelog"),
    ("About", "about.html", "about"),
]
GUIDE_PAGES = [
    ("guide.html", "Overview"),
    ("being-pragmatic.html", "Being Pragmatic"),
    ("field-guide.html", "Field Guide"),
    ("glossary.html", "Glossary"),
    ("bibliography.html", "Bibliography"),
]
FONTS = (
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
    "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400"
    "&family=Public+Sans:wght@400;500;600&display=swap"
)


# ---------------------------------------------------------------- text helpers
def esc(s):
    return html.escape(s, quote=True)


def typo(s):
    s = re.sub(r"(\w)'(\w)", "\\1\u2019\\2", s)
    s = re.sub(r'(^|[\s(\[\u2014-])"', "\\1\u201c", s)
    s = s.replace('"', "\u201d")
    s = re.sub(r"(^|[\s(\[\u2014-])'", "\\1\u2018", s)
    return s.replace("'", "\u2019")


def unescape_md(s):
    return re.sub(r"\\([^A-Za-z0-9\s*_])", r"\1", s)


def inline(s):
    """Inline markdown (bold, italic, links) to HTML. Text is smart-quoted and escaped."""
    links = []

    def grab(m):
        links.append((m.group(1), re.sub(r"\\(.)", r"\1", m.group(2))))
        return "\x03%d\x03" % (len(links) - 1)

    s = re.sub(r"\[((?:\\.|[^\]\\])+)\]\(((?:\\.|[^)\\])+)\)", grab, s)
    s = unescape_md(s)
    s = s.replace("\\*", "\x01").replace("\\_", "\x02")
    s = esc(typo(s))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = s.replace("\x01", "*").replace("\x02", "_")

    def put(m):
        text, url = links[int(m.group(1))]
        return '<a href="%s" rel="noopener">%s</a>' % (esc(url), esc(typo(text)))

    return re.sub("\x03(\\d+)\x03", put, s)


def plain(s):
    s = unescape_md(s).replace("\\*", "*").replace("\\_", "_")
    s = re.sub(r"\[((?:[^\]])+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<![\w*])\*(.+?)\*(?![\w*])", r"\1", s)
    return s.replace("\u00a0", " ")


def txt(s):
    """Plain text from importer strings that may keep \\* or \\_ escapes."""
    return s.replace("\\*", "*").replace("\\_", "_")


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", plain(s).lower().replace("'", ""))
    return s.strip("-")


def fmt_date(iso, short=False):
    d = datetime.date.fromisoformat(iso)
    return "%d %s %d" % (d.day, d.strftime("%b"), d.year) if not short else "%d %s" % (d.day, d.strftime("%b"))


# ---------------------------------------------------------------- data prep
def sentences(text):
    """Split into sentences without breaking after 'et al.' or inside '(2016)'."""
    return re.split(r'(?<!al\.)(?<=[.?!])\s+(?=[A-Z\u201c"])', text)


def prep_laws():
    glossary_by_law = collections.defaultdict(list)
    for g in GLOSS:
        for name in g["see"]:
            glossary_by_law[name].append(g)
    keysets = []
    for law in LAWS:
        keysets.append({re.sub(r"[^a-z0-9]", "", s["title"].lower()) for s in law["sources"]})
    for i, law in enumerate(LAWS):
        ed = EDIT["laws"][law["slug"]]
        law["roles"] = ed["roles"]
        law["plainTerms"] = ed["plainTerms"]
        law["questions"] = ed["questions"]
        law["alsoKnownAs"] = ed.get("alsoKnownAs", [])
        law["workedExample"] = ed.get("workedExample")
        d = SITE["lawDefaults"]
        law["published"] = ed.get("published", d["published"])
        law["revised"] = ed.get("revised")
        law["version"] = ed.get("version", d["version"])
        law["evidenceChecked"] = ed.get("evidenceChecked", d["evidenceChecked"])
        law["history"] = ed.get("history") or [{"v": law["version"], "d": law["published"], "t": "Published."}]
        law["terms"] = glossary_by_law.get(law["name"], [])
        scores = []
        for j, other in enumerate(LAWS):
            if j == i:
                continue
            shared = len(keysets[i] & keysets[j])
            if shared:
                same_cat = 1 if other["category"] == law["category"] else 0
                scores.append((-shared, -same_cat, abs(j - i), j))
        law["shared"] = [[LAWS[j]["no"], n] for n, j in sorted(((len(keysets[i] & keysets[j]), j) for j in range(len(LAWS)) if j != i and keysets[i] & keysets[j]), key=lambda t: (-t[0], t[1]))]
        item, idxs = EDIT["briefEvidence"][law["slug"]]
        ev_sentences = sentences(plain(law["evidence"][item]["text"]))
        law["evidenceLine"] = typo(" ".join(ev_sentences[k] for k in idxs))
        law["doIt"] = typo(plain(law["useIt"][0]))
        scores.sort()
        related = [LAWS[s[3]]["slug"] for s in scores[:3]]
        fill = sorted((j for j in range(len(LAWS)) if j != i and LAWS[j]["slug"] not in related), key=lambda j: (LAWS[j]["category"] != law["category"], abs(j - i)))
        law["related"] = (related + [LAWS[j]["slug"] for j in fill])[:3]
    by_slug = {l["slug"]: l for l in LAWS}
    return by_slug


BY_SLUG = prep_laws()
NAMES = sorted([(l["name"], l["slug"]) for l in LAWS], key=lambda t: -len(t[0]))
PAGE_LINKS = {"Overview": "guide.html", "Being Pragmatic": "being-pragmatic.html", "Field Guide": "field-guide.html", "Glossary": "glossary.html"}


def link_laws(h, prefix=""):
    """Link law names and guide page names found in text nodes (outside existing anchors)."""
    parts = re.split(r"(<[^>]+>)", h)
    out, in_a = [], 0
    targets = [(typo(n), "laws/%s.html" % s) for n, s in NAMES] + [(typo(n), href) for n, href in PAGE_LINKS.items() if n in ("Being Pragmatic", "Field Guide")]
    targets.sort(key=lambda t: -len(t[0]))
    pattern = re.compile("|".join(re.escape(n) for n, _ in targets))
    lookup = dict(targets)
    for part in parts:
        if part.startswith("<"):
            if part.startswith("<a "):
                in_a += 1
            elif part.startswith("</a"):
                in_a -= 1
            out.append(part)
        elif in_a:
            out.append(part)
        else:
            out.append(pattern.sub(lambda m: '<a href="%s%s">%s</a>' % (prefix, lookup[m.group(0)], m.group(0)), part))
    return "".join(out)


def law_url(slug, prefix=""):
    return "%slaws/%s.html" % (prefix, slug)


# ---------------------------------------------------------------- markdown blocks
def md_blocks(lines, prefix="", h2="###"):
    out, i = [], 0
    h3 = h2 + "#"
    lines = [l.replace("\u00a0", " ") for l in lines]

    def is_block_start(ln):
        return ln.startswith("#") or ln.startswith("|") or ln.startswith("- ") or re.match(r"^\d+\\?\.\s", ln) or ln.startswith("> ")

    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith(h3 + " "):
            text = unescape_md(ln[len(h3) + 1 :])
            out.append('<h3 id="%s">%s</h3>' % (slugify(text), inline(text)))
            i += 1
        elif ln.startswith(h2 + " "):
            text = unescape_md(ln[len(h2) + 1 :])
            out.append('<h2 id="%s">%s</h2>' % (slugify(text), inline(text)))
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-+:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            t = "<div class=\"table-wrap\"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>" % (
                "".join("<th scope=\"col\">%s</th>" % link_laws(inline(c), prefix) for c in head),
                "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % link_laws(inline(c), prefix) for c in r) for r in body),
            )
            out.append(t)
        elif ln.startswith("- ") or re.match(r"^\d+\\?\.\s", ln):
            ordered = not ln.startswith("- ")
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or re.match(r"^\d+\\?\.\s", lines[i]) or (lines[i].startswith("  ") and lines[i].strip())):
                cur = lines[i]
                if cur.startswith("  "):
                    items[-1] += " " + cur.strip()
                else:
                    items.append(re.sub(r"^(- |\d+\\?\.\s)", "", cur).rstrip())
                i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % link_laws(inline(x), prefix) for x in items), tag))
        elif ln.startswith("> "):
            out.append("<blockquote>%s</blockquote>" % inline(ln[2:]))
            i += 1
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]):
                buf.append(lines[i].strip())
                i += 1
            if not buf:
                buf = [lines[i].strip()]
                i += 1
            out.append("<p>%s</p>" % link_laws(inline(" ".join(buf)), prefix))
    return "\n".join(out)


MANUSCRIPT = (SRC / "laws-of-ai-evaluation-full.md").read_text(encoding="utf-8").split("\n")


def manuscript_region(start, end):
    a = next(i for i, l in enumerate(MANUSCRIPT) if l.strip() == start)
    b = next((i for i, l in enumerate(MANUSCRIPT) if i > a and l.strip() == end), len(MANUSCRIPT))
    return MANUSCRIPT[a + 1 : b]


# ---------------------------------------------------------------- layout
def layout(title, desc, body, depth=0, current=None, scripts=(), data=False, skip="Skip to content", page_class="", head_extra=""):
    p = "../" * depth
    full_title = title if title == SITE["title"] else "%s \u00b7 %s" % (title, SITE["title"])
    nav = "".join(
        '<a href="%s%s"%s>%s</a>' % (p, href, ' aria-current="page"' if key == current else "", label) for label, href, key in NAV
    )
    scripts_html = ""
    if data:
        scripts_html += '<script src="%sjs/data.js"></script>\n' % p
    scripts_html += '<script src="%sjs/collection.js" defer></script>\n' % p
    scripts_html += '<script src="%sjs/site.js" defer></script>\n' % p
    for s in scripts:
        scripts_html += '<script src="%sjs/%s" defer></script>\n' % (p, s)
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%%3E%%3Crect width='32' height='32' fill='%%239b2f1f'/%%3E%%3Ctext x='16' y='23' font-size='20' text-anchor='middle' fill='%%23faf7f1' font-family='Georgia,serif'%%3E\u00a7%%3C/text%%3E%%3C/svg%%3E">
<link rel="alternate" type="application/rss+xml" title="%(site)s changelog" href="%(p)sfeed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="%(fonts)s">
<link rel="stylesheet" href="%(p)scss/tokens.css">
<link rel="stylesheet" href="%(p)scss/styles.css">
%(head_extra)s</head>
<body class="%(page_class)s" data-root="%(p)s">
<a class="skip-link" href="#main">%(skip)s</a>
<header class="site-header">
  <a class="wordmark" href="%(p)sindex.html"><span class="wordmark__mark" aria-hidden="true">\u00a7</span><span class="wordmark__text">Laws of AI Evaluation</span></a>
  <nav class="site-nav" id="site-nav" aria-label="Primary">%(nav)s</nav>
  <button class="search-trigger" type="button" data-search-open aria-haspopup="dialog"><span>Search laws</span><kbd data-kbd>\u2318K</kbd></button>
  <div class="header-actions">
    <button class="icon-btn" type="button" data-search-open aria-haspopup="dialog">Find</button>
    <button class="icon-btn" type="button" data-menu-toggle aria-expanded="false" aria-controls="site-nav">Menu</button>
  </div>
</header>
%(body)s
<footer class="site-footer">
  <p>Independent reference. No vendor funding. <a href="%(p)sabout.html#editorial-policy">Editorial policy</a></p>
  <p>CC BY 4.0 \u00b7 <a href="%(p)sfeed.xml">RSS</a> \u00b7 Last updated %(updated)s</p>
</footer>
%(scripts)s</body>
</html>
""" % {
        "title": esc(full_title),
        "desc": esc(desc),
        "site": esc(SITE["title"]),
        "p": p,
        "fonts": FONTS,
        "nav": nav,
        "body": body,
        "skip": esc(skip),
        "updated": fmt_date(SITE["updated"]),
        "scripts": scripts_html,
        "page_class": page_class,
        "head_extra": head_extra,
    }


def write(rel, content):
    if rel.endswith(".html"):
        url = SITE["baseUrl"] + "/" + ("" if rel == "index.html" else rel[: -len(".html")])
        tags = '<link rel="canonical" href="%s">\n<meta property="og:url" content="%s">\n' % (url, url)
        content = content.replace("</head>", tags + "</head>", 1)
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def roman_label(cat_id):
    return cat_id + "."


# ---------------------------------------------------------------- index
def pick_button(law, cls="pick", off="Add", on="Added"):
    name = esc(typo(law["name"]))
    return (
        '<button class="%s" type="button" data-pick="%d" data-name="%s" data-label-off="%s" data-label-on="%s" aria-pressed="false">'
        '<span class="pick__mark" aria-hidden="true">+</span><span class="pick__text">%s</span><span class="visually-hidden"> (%s)</span></button>' % (cls, int(law["no"]), name, off, on, off, name)
    )


def law_card(law, prefix=""):
    cat = CAT[law["category"]]
    return (
        '<li class="law-item"><a class="law-card cat-%d" href="%s" data-no="%s" data-roles="%s" data-published="%s" data-revised="%s">'
        '<span class="law-card__row"><span class="law-card__no">No. %s</span><span class="badge" data-badge hidden></span>'
        '<span class="tag">%s</span></span>'
        '<span class="law-card__title">%s</span>'
        '<span class="law-card__quote">\u201c%s\u201d</span>'
        '<span class="law-card__cta">Read the law \u2192</span></a>%s</li>'
        % (
            cat["n"],
            law_url(law["slug"], prefix),
            law["no"],
            esc(" ".join(r.lower() for r in law["roles"])),
            law["published"],
            law["revised"] or "",
            law["no"],
            esc(cat["short"]),
            esc(typo(law["name"])),
            esc(typo(law["aphorism"])),
            pick_button(law),
        )
    )


def build_index():
    total = len(LAWS)
    sections, columns = [], []
    chips = []
    for c in CATS:
        laws = [l for l in LAWS if l["category"] == c["id"]]
        cards = "".join(law_card(l) for l in laws)
        sections.append(
            '<section class="category cat-%d" id="cat-%s" aria-labelledby="cat-%s-h">'
            '<div class="category__head"><span class="category__num">%s</span><h2 id="cat-%s-h">%s</h2>'
            '<span class="category__count" data-count data-total="%d">%d of %d published</span></div>'
            '<ul class="card-grid">%s</ul></section>' % (c["n"], c["id"], c["id"], roman_label(c["id"]), c["id"], esc(typo(c["name"])), len(laws), len(laws), len(laws), cards)
        )
        entries = "".join(
            '<li class="law-item"><a class="catcol__entry" href="%s" data-no="%s" data-roles="%s" data-published="%s" data-revised="%s">'
            '<span class="catcol__no">No. %s<span class="badge" data-badge hidden></span></span>'
            '<span class="catcol__title">%s</span><span class="catcol__quote">\u201c%s\u201d</span></a>%s</li>'
            % (law_url(l["slug"]), l["no"], esc(" ".join(r.lower() for r in l["roles"])), l["published"], l["revised"] or "", l["no"], esc(typo(l["name"])), esc(typo(l["aphorism"])), pick_button(l, "pick pick--corner", "Add", "Added"))
            for l in laws
        )
        columns.append(
            '<li class="catcol cat-%d"><details open><summary><span class="catcol__sq" aria-hidden="true"></span>'
            '<span class="catcol__head"><span class="catcol__meta"><span class="catcol__roman">%s</span> \u00b7 <span data-count data-total="%d">%d of %d</span></span>'
            '<span class="catcol__name">%s</span></span><span class="catcol__toggle" aria-hidden="true"></span></summary>'
            '<ul class="catcol__list">%s</ul></details></li>' % (c["n"], c["id"], len(laws), len(laws), len(laws), esc(typo(c["name"])), entries)
        )
        chips.append('<a class="chip cat-%d" href="#cat-%s"><span class="chip__sq" aria-hidden="true"></span>%s</a>' % (c["n"], c["id"], c["id"]))

    body = """<main id="main" data-page="index" data-view="grid" data-total="%(total)d" data-updated="%(updated)s">
  <section class="hero" data-hero="grid">
    <div class="hero__text">
      <h1>Principles for judging whether an AI system <em>actually</em> holds up.</h1>
      <p class="hero__sub">%(total)d short, sourced laws for people who build, buy, or design with AI. <a href="guide.html">How to use this guide</a></p>
    </div>
    <p class="hero__meta"><span data-published-count>%(total)d of %(total)d published</span><br>Updated %(updated_h)s \u00b7 <a href="feed.xml">RSS</a></p>
  </section>
  <section class="hero hero--category" data-hero="category" hidden>
    <h1>All laws, by where they bite</h1>
  </section>
  <div class="since" data-since hidden>
    <span class="since__badge" data-since-badge></span>
    <span data-since-text></span>
    <a href="changelog.html">See what changed</a>
    <button class="since__dismiss" type="button" data-since-dismiss>Dismiss</button>
  </div>
  <div class="toolbar">
    <div class="seg seg--ink" role="group" aria-label="View">
      <button type="button" data-view-btn="grid" aria-pressed="true">Grid</button>
      <button type="button" data-view-btn="category" aria-pressed="false">By category</button>
    </div>
    <div class="seg seg--rule" role="group" aria-label="Filter by role">
      <button type="button" data-role-btn="all" aria-pressed="true">All roles</button>
      <button type="button" data-role-btn="building" aria-pressed="false">Building</button>
      <button type="button" data-role-btn="buying" aria-pressed="false">Buying</button>
      <button type="button" data-role-btn="designing" aria-pressed="false">Designing</button>
    </div>
    <a class="btn btn--outline btn--sm toolbar__brief" href="brief.html" data-collection-link="brief.html">Quick brief<span data-collection-badge hidden> (<span data-collection-count>0</span>)</span></a>
    <div class="toolbar__jump" data-jump><span class="toolbar__label">Jump to</span>%(chips)s</div>
    <p class="visually-hidden" role="status" aria-live="polite" data-status></p>
  </div>
  <div data-view-panel="grid">%(sections)s</div>
  <div class="catview" data-view-panel="category" hidden><ul class="catview__grid">%(columns)s</ul></div>
</main>
<div class="tray no-print" data-tray hidden role="region" aria-label="My laws">
  <p class="tray__count"><strong data-collection-count>0</strong> <span data-tray-word>laws</span> in My laws</p>
  <div class="tray__actions">
    <a class="btn btn--accent btn--sm" href="brief.html" data-collection-link="brief.html">Quick brief</a>
    <a class="btn btn--outline btn--sm" href="checklist.html?preset=custom" data-collection-link="checklist.html?preset=custom">Checklist</a>
    <button class="btn btn--ghost btn--sm" type="button" data-tray-clear>Clear</button>
  </div>
</div>
""" % {
        "total": total,
        "updated": SITE["updated"],
        "updated_h": fmt_date(SITE["updated"]),
        "chips": "".join(chips),
        "sections": "".join(sections),
        "columns": "".join(columns),
    }
    write(
        "index.html",
        layout(
            SITE["title"],
            "%d short, sourced laws for people who build, buy, or design with AI: principles for judging whether an AI system actually holds up." % len(LAWS),
            body,
            current="laws",
            scripts=("index.js",),
            skip="Skip to laws",
        ),
    )


# ---------------------------------------------------------------- law pages
SECTION_TOC = [
    ("plain-terms", "In plain terms"),
    ("takeaways", "Takeaways"),
    ("what-it-means", "What it means"),
    ("the-evidence", "The evidence"),
    ("use-it", "Use it"),
    ("questions-to-ask", "Questions to ask"),
    ("origins", "Origins"),
    ("sources", "Sources"),
    ("cite-this-law", "Cite this law"),
    ("revision-history", "Revision history"),
]


def source_mix(law):
    c = collections.Counter(s["label"] or "peer" for s in law["sources"])
    parts = []
    if c["peer"]:
        parts.append("%d peer-reviewed or classic" % c["peer"])
    for key, one, many in (("Preprint", "preprint", "preprints"), ("Report", "report", "reports"), ("Working paper", "working paper", "working papers"), ("Book", "book", "books")):
        if c[key]:
            parts.append("%d %s" % (c[key], one if c[key] == 1 else many))
    return ", ".join(parts)


def apa(law):
    d = datetime.date.fromisoformat(law["published"])
    return "Laws of AI Evaluation. (%d, %s %d). %s (%s). %s/laws/%s" % (d.year, d.strftime("%B"), d.day, law["name"], law["version"], SITE["baseUrl"], law["slug"])


def bibtex(law):
    d = datetime.date.fromisoformat(law["published"])
    return (
        "@misc{lai-%s,\n  title        = {%s},\n  author       = {{Laws of AI Evaluation}},\n  year         = {%d},\n  month        = %s,\n"
        "  note         = {Version %s},\n  howpublished = {\\url{%s/laws/%s}}\n}"
        % (law["slug"], law["name"], d.year, d.strftime("%b").lower(), law["version"].lstrip("v"), SITE["baseUrl"], law["slug"])
    )


def build_law(i, law):
    cat = CAT[law["category"]]
    cat_laws = [l for l in LAWS if l["category"] == law["category"]]
    pos = cat_laws.index(law) + 1
    nxt = LAWS[i + 1] if i + 1 < len(LAWS) else None
    url = "%s/laws/%s" % (SITE["baseUrl"], law["slug"])
    cat_href = "../index.html#cat-%s" % cat["id"]

    toc = "".join(
        '<li><a href="#%s" data-toc="%s"><span class="toc__n">%02d</span><span>%s</span></a></li>' % (sid, sid, n + 1, label)
        for n, (sid, label) in enumerate(SECTION_TOC)
    )
    related = "".join(
        '<li><a href="%s.html"><span class="related__n">%s</span> <span class="related__t">%s</span></a></li>' % (s, BY_SLUG[s]["no"], esc(typo(BY_SLUG[s]["name"])))
        for s in law["related"]
    )

    def h2(sid, text, extra=""):
        return '<div class="sec-head"><h2 id="%s">%s <a class="permalink" href="#%s" aria-label="Link to %s">#</a></h2>%s</div>' % (sid, text, sid, esc(text), extra)

    takeaways = "".join("<li>%s</li>" % inline(t) for t in law["takeaways"])
    means = "".join("<p>%s</p>" % inline(p) for p in law["whatItMeans"])
    evidence = "".join("<p>%s%s</p>" % ("<strong>%s</strong> " % inline(e["lead"]) if e["lead"] else "", inline(e["text"])) for e in law["evidence"])
    use_it = "".join("<li>%s</li>" % inline(t) for t in law["useIt"])
    questions = "".join(
        '<li><label class="qrow"><input type="checkbox"><span class="qrow__box" aria-hidden="true"></span><span>%s</span></label></li>' % esc(typo(q)) for q in law["questions"]
    )
    origins = "".join("<p>%s</p>" % inline(p) for p in law["origins"])
    sources = ""
    for n, s in enumerate(law["sources"], 1):
        label = ' <span class="src__label">%s</span>' % esc(s["label"]) if s["label"] else ""
        open_link = '<a class="src__open" href="%s" target="_blank" rel="noopener">Open \u2197<span class="visually-hidden"> (opens in a new tab)</span></a>' % esc(s["url"]) if s["url"] else '<span class="src__open src__open--none">No link</span>'
        sources += (
            '<li id="src-%d"><span class="src__n">[%d]</span><div class="src__body"><cite>%s (%s). <em>%s</em>.</cite>'
            '<span class="src__venue">%s%s</span></div>%s</li>'
            % (n, n, esc(typo(txt(s["authors"]))), s["year"], esc(typo(txt(s["title"]))), esc(typo(txt(s["venue"]))), label, open_link)
        )
    history = "".join('<li><span class="rev__v">%s</span><span class="rev__d">%s</span><span class="rev__t">%s</span></li>' % (esc(h["v"]), fmt_date(h["d"]), esc(h["t"])) for h in law["history"])

    cite_apa, cite_bib = apa(law), bibtex(law)
    cite = """<div class="cite" data-cite>
  <div class="cite__tabs">
    <div class="cite__tablist" role="tablist" aria-label="Citation format">
      <button type="button" role="tab" id="tab-apa" aria-selected="true" aria-controls="panel-apa" data-tab="apa">APA</button>
      <button type="button" role="tab" id="tab-bibtex" aria-selected="false" aria-controls="panel-bibtex" tabindex="-1" data-tab="bibtex">BibTeX</button>
      <button type="button" role="tab" id="tab-link" aria-selected="false" aria-controls="panel-link" tabindex="-1" data-tab="link">Permalink</button>
    </div>
    <button class="btn btn--ink cite__copy" type="button" data-copy>Copy</button>
  </div>
  <div role="tabpanel" id="panel-apa" aria-labelledby="tab-apa" data-panel="apa"><pre><code>%s</code></pre></div>
  <div role="tabpanel" id="panel-bibtex" aria-labelledby="tab-bibtex" data-panel="bibtex" hidden><pre><code>%s</code></pre></div>
  <div role="tabpanel" id="panel-link" aria-labelledby="tab-link" data-panel="link" hidden><pre><code>%s</code></pre></div>
</div>""" % (esc(cite_apa), esc(cite_bib), esc(url))

    plain_box = '<section class="plain" aria-labelledby="plain-terms"><h2 class="plain__label" id="plain-terms">In plain terms</h2><p>%s</p></section>' % esc(typo(law["plainTerms"]))

    trust = (
        '<dl class="trust">'
        '<div><dt>Last reviewed</dt><dd>%s</dd></div>'
        '<div><dt>Sources</dt><dd><a href="#sources">%d</a> \u00b7 <a href="#cite-this-law">Cite</a></dd></div>'
        '<div><dt>Source types</dt><dd class="trust__small">%s</dd></div>'
        '<div><dt>Version</dt><dd>%s <span class="trust__small">%s</span></dd></div></dl>'
        % (fmt_date(law["evidenceChecked"]), len(law["sources"]), esc(source_mix(law)), esc(law["version"]), fmt_date(law["published"]))
    )

    # right column
    aside = []
    if law["workedExample"]:
        aside.append(
            '<details class="aside-block" open><summary>Worked example</summary><p class="aside__serif">%s</p><p class="aside__note">%s</p></details>'
            % (esc(typo(law["workedExample"]["text"])), esc(typo(law["workedExample"]["note"])))
        )
    if law["terms"]:
        terms = "".join("<dt>%s</dt><dd>%s</dd>" % (esc(typo(t["term"])), inline(t["definition"])) for t in law["terms"][:4])
        aside.append('<details class="aside-block" open><summary>Terms used here</summary><dl class="terms">%s</dl></details>' % terms)
    if law["alsoKnownAs"]:
        aside.append('<details class="aside-block" open><summary>Also known as</summary><ul class="chips">%s</ul></details>' % "".join("<li>%s</li>" % esc(typo(a)) for a in law["alsoKnownAs"]))
    aside.append(
        '<details class="aside-block" open><summary>Take it with you</summary><ul class="takeaway">'
        '<li><a href="../brief.html?laws=%s" data-collection-link="../brief.html" data-collection-extra="%s">Quick brief <span>Short overview</span></a></li>'
        '<li><a href="../checklist.html?preset=custom&amp;laws=%s" data-collection-link="../checklist.html?preset=custom" data-collection-extra="%s">Printable checklist <span>Print \u00b7 PDF</span></a></li>'
        '<li><a href="#cite-this-law">Cite this law <span>APA \u00b7 BibTeX</span></a></li></ul></details>' % (law["no"], law["no"], law["no"], law["no"])
    )

    prev_box = '<a class="pn pn--prev" href="%s"><span class="pn__k">\u2190 Back to category</span><span class="pn__t">%s. %s</span></a>' % (cat_href, cat["id"], esc(typo(cat["name"])))
    if nxt:
        next_box = '<a class="pn pn--next" href="%s.html"><span class="pn__k">Next law \u2192</span><span class="pn__t">%s %s</span></a>' % (nxt["slug"], nxt["no"], esc(typo(nxt["name"])))
        crumb_next = '<a class="btn btn--outline btn--sm" href="%s.html">Next: %s %s \u2192</a>' % (nxt["slug"], nxt["no"], esc(typo(nxt["name"])))
        bar_next = '<a href="%s.html">Next: %s \u2192</a>' % (nxt["slug"], nxt["no"])
    else:
        next_box = '<a class="pn pn--next" href="../index.html"><span class="pn__k">All laws \u2192</span><span class="pn__t">Back to the index</span></a>'
        crumb_next = '<a class="btn btn--outline btn--sm" href="../index.html">All laws \u2192</a>'
        bar_next = '<a href="../index.html">All laws \u2192</a>'

    body = """<div class="crumbs"><nav aria-label="Breadcrumb"><ol>
    <li><a href="../index.html">Laws</a></li><li><a href="%(cat_href)s">%(cat_id)s. %(cat_name)s</a></li><li aria-current="page">No. %(no)s</li></ol></nav>
    <div class="crumbs__right"><span>%(pos)d of %(cat_total)d in this category</span>%(crumb_next)s</div></div>
<main id="main" class="law-layout cat-%(cat_n)d" data-page="law" data-no="%(no)s" data-slug="%(slug)s">
  <aside class="law-rail" aria-label="On this page">
    <details class="toc" open><summary>On this page <span aria-hidden="true" class="toc__plus"></span></summary><ol>%(toc)s</ol></details>
    <div class="related"><h2 class="rail-label">Related</h2><ul>%(related)s</ul></div>
  </aside>
  <article class="law">
    <div class="law__meta"><span class="law__no">No. %(no)s</span><a class="tag" href="%(cat_href)s">%(cat_short)s</a><span class="chip-ver">%(version)s</span>%(pick)s<span class="law__for">For: %(roles)s</span></div>
    <h1 class="law__title">%(name)s</h1>
    <blockquote class="law__quote"><p>\u201c%(aphorism)s\u201d</p></blockquote>
    %(trust)s
    %(plain)s
    <section class="sec" aria-labelledby="takeaways">%(h_take)s<ul class="dash">%(takeaways)s</ul></section>
    <section class="sec" aria-labelledby="what-it-means">%(h_means)s%(means)s</section>
    <section class="sec" aria-labelledby="the-evidence">%(h_evid)s%(evidence)s</section>
    <section class="sec" aria-labelledby="use-it">%(h_use)s<ol class="num">%(use_it)s</ol></section>
    <section class="sec" aria-labelledby="questions-to-ask">%(h_q)s<p class="sec__sub">For vendor reviews, model cards, and launch reviews.</p><ul class="qlist">%(questions)s</ul></section>
    <section class="sec" aria-labelledby="origins">%(h_orig)s%(origins)s</section>
    <section class="sec" aria-labelledby="sources">%(h_src)s<ol class="sources">%(sources)s</ol></section>
    <section class="sec" aria-labelledby="cite-this-law">%(h_cite)s%(cite)s</section>
    <section class="sec" aria-labelledby="revision-history">%(h_rev)s<ul class="rev">%(history)s</ul><p class="rev__links"><a href="../changelog.html">Full changelog</a></p></section>
    <nav class="pn-row" aria-label="Previous and next law">%(prev_box)s%(next_box)s</nav>
  </article>
  <aside class="law-aside" aria-label="Supporting material"><h2 class="aside-title">Supporting material</h2>%(aside)s</aside>
</main>
<div class="law-bar" aria-label="Law navigation"><a href="%(cat_href)s">\u2190 Category</a><a href="#cite-this-law">Cite</a>%(bar_next)s</div>
""" % {
        "cat_href": cat_href,
        "cat_id": cat["id"],
        "cat_name": esc(typo(cat["name"])),
        "cat_short": esc(cat["short"]),
        "cat_n": cat["n"],
        "no": law["no"],
        "pos": pos,
        "cat_total": len(cat_laws),
        "crumb_next": crumb_next,
        "toc": toc,
        "related": related,
        "version": esc(law["version"]),
        "pick": pick_button(law, "pick pick--inline", "Add to My laws", "In My laws"),
        "roles": " \u00b7 ".join(law["roles"]),
        "name": esc(typo(law["name"])),
        "aphorism": esc(typo(law["aphorism"])),
        "slug": law["slug"],
        "trust": trust,
        "plain": plain_box,
        "h_take": h2("takeaways", "Takeaways"),
        "takeaways": takeaways,
        "h_means": h2("what-it-means", "What it means"),
        "means": means,
        "h_evid": h2("the-evidence", "The evidence", '<span class="sec-head__note">reviewed %s</span>' % fmt_date(law["evidenceChecked"])),
        "evidence": evidence,
        "h_use": h2("use-it", "Use it"),
        "use_it": use_it,
        "h_q": h2("questions-to-ask", "Questions to ask", '<div class="sec-head__actions">%s<a class="btn btn--ink btn--sm" href="../checklist.html?preset=custom&amp;laws=%s" data-collection-link="../checklist.html?preset=custom" data-collection-extra="%s">Print checklist</a></div>' % (pick_button(law, "pick pick--btn", "Add to My laws", "In My laws"), law["no"], law["no"])),
        "questions": questions,
        "h_orig": h2("origins", "Origins"),
        "origins": origins,
        "h_src": h2("sources", "Sources"),
        "sources": sources,
        "h_cite": h2("cite-this-law", "Cite this law"),
        "cite": cite,
        "h_rev": h2("revision-history", "Revision history"),
        "history": history,
        "prev_box": prev_box,
        "next_box": next_box,
        "aside": "".join(aside),
        "bar_next": bar_next,
    }
    page = layout(law["name"], "%s %s" % (law["aphorism"], law["plainTerms"]), body, depth=1, current="laws", scripts=("law.js",))
    write("laws/%s.html" % law["slug"], page)


# ---------------------------------------------------------------- tools data
def parse_rubric():
    groups, cur = [], None
    for ln in (SRC / "ai-design-evaluation-rubric.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (.+?) \u2014 (.+?) \(\u2014\)$", ln)
        if m:
            cur = {"name": m.group(1), "tagline": m.group(2), "items": []}
            groups.append(cur)
        elif ln.startswith("- [\u2014] ") and cur is not None:
            cur["items"].append(ln[len("- [\u2014] ") :])
    initials = {"Agency": "A", "Transparency": "T", "Honesty": "H", "Equity": "E", "Real reduction": "R", "Failure design": "F"}
    for g in groups:
        g["code"] = initials[g["name"]]
        g["items"] = [{"id": "%s%d" % (g["code"], n), "text": t} for n, t in enumerate(g["items"], 1)]
    return groups


def load_airr():
    return json.loads((SRC / "ai-readiness-review.json").read_text(encoding="utf-8"))


RUBRIC = parse_rubric()
AIRR = load_airr()


def tool_page(title, desc, current, intro_html, sections_html, source_note):
    body = """<main id="main" class="page page--tool">
  <header class="page__head"><p class="eyebrow">Tool</p><h1>%s</h1>%s</header>
  %s
  <p class="page__note">%s</p>
</main>""" % (esc(title), intro_html, sections_html, source_note)
    return layout(title, desc, body, current=current)


def build_rubric():
    secs = []
    for g in RUBRIC:
        items = "".join('<li id="%s"><span class="crit__id">%s</span><span class="crit__text">%s</span></li>' % (i["id"], i["id"], esc(typo(i["text"]))) for i in g["items"])
        secs.append(
            '<section class="tool-sec" aria-labelledby="g-%s"><h2 id="g-%s"><span class="tool-sec__code">%s</span>%s <span class="tool-sec__tag">\u2014 %s</span></h2><ol class="crit">%s</ol></section>'
            % (g["code"], g["code"], g["code"], esc(typo(g["name"])), esc(typo(g["tagline"])), items)
        )
    intro = (
        '<p class="page__lede">A quick scoring checklist for judging a single AI feature or design. Each of the six groups has three checks. '
        'Use it in a design critique or before a launch review, then follow the checks that fail back to the laws.</p>'
    )
    note = "This page lists the checks. Interactive scoring is planned; see the <a href=\"changelog.html\">Changelog</a>. Check numbers (A1, T2, and so on) are labels used on this site."
    write("design-rubric.html", tool_page("AI Design Evaluation Rubric", "An 18-check rubric for evaluating an AI feature across agency, transparency, honesty, equity, real reduction, and failure design.", "rubric", intro, "".join(secs), note))


REVIEW_SOURCES = {
    "HAX G1\u2013G18": "Microsoft\u2019s Guidelines for Human-AI Interaction, eighteen guidelines for how an AI feature should behave with the people using it.",
    "NIST AI 100-1": "NIST\u2019s AI Risk Management Framework 1.0, a U.S. framework for identifying and managing AI risk.",
    "NIST AI 600-1": "NIST\u2019s Generative AI Profile, which applies the AI Risk Management Framework to generative AI.",
    "PAIR Guidebook": "Google\u2019s People + AI Guidebook, design guidance for AI-powered products.",
    "AI Act Art. 13": "EU AI Act, Article 13: transparency and the information a system must provide to the people who deploy it.",
    "AI Act Art. 14": "EU AI Act, Article 14: human oversight of high-risk AI systems.",
    "AI Act Art. 50": "EU AI Act, Article 50: transparency duties, including telling people when they are interacting with an AI system.",
    "ISO/IEC 42001": "The international standard for AI management systems.",
    "WCAG 2.2": "W3C\u2019s Web Content Accessibility Guidelines, version 2.2.",
    "W3C AI-A11y": "W3C work on accessibility and AI.",
    "Parasuraman 1997": "Parasuraman and Riley (1997), research on how people use, over-rely on, and neglect automation.",
    "Mosier 1996": "Mosier and Skitka (1996), research on automation bias in human decision-making.",
}


def src_id(ref):
    return "src-" + re.sub(r"[^a-z0-9]+", "-", ref.lower()).strip("-")


def build_review():
    dims = {d["code"]: d for d in AIRR["dimensions"]}
    screening = "".join('<li id="%s"><span class="crit__id">%s</span><span class="crit__text">%s</span></li>' % (s["id"], s["id"].upper(), esc(typo(s["question"]))) for s in AIRR["screening"])
    secs = ['<section class="tool-sec" aria-labelledby="screening"><h2 id="screening"><span class="tool-sec__code">1</span>Screening <span class="tool-sec__tag">\u2014 five questions asked before scoring</span></h2><ol class="crit">%s</ol></section>' % screening]
    for code in sorted(dims):
        crits = [c for c in AIRR["criteria"] if c["dimension"] == code]
        rows = ""
        for c in crits:
            gate = '<span class="gate">Gate \u00b7 T%d</span>' % c["gateTier"] if c["gateTier"] else ""
            refs = "".join('<li><a href="#%s">%s</a></li>' % (src_id(r), esc(r)) for r in c["references"])
            rows += '<li id="%s"><span class="crit__id">%s</span><span class="crit__text">%s<span class="crit__meta">%s<span class="crit__label" id="%s-src">Based on</span><ul class="refs" aria-labelledby="%s-src">%s</ul></span></span></li>' % (c["id"], c["id"], esc(typo(c["criterion"])), gate, c["id"], c["id"], refs)
        secs.append(
            '<section class="tool-sec" aria-labelledby="%s"><h2 id="%s"><span class="tool-sec__code">%s</span>%s</h2><ol class="crit">%s</ol></section>'
            % (code, code, code, esc(typo(dims[code]["title"])), rows)
        )
    intro = (
        '<p class="page__lede">A more rigorous instrument for launch review. Five screening questions come first, then 27 criteria across seven dimensions. '
        'Under each criterion, the labels marked "Based on" name the standards and guidelines it draws on; the key at the bottom of the page explains each one. Some criteria are marked as gates.</p>'
    )
    note = "This page lists the instrument (AIRR v%s). Tier routing and scoring are not built here yet; see the <a href=\"changelog.html\">Changelog</a>. A Gate badge shows the risk tier recorded for that criterion in the instrument." % esc(AIRR["instrument"]["version"])
    used = []
    for c in AIRR["criteria"]:
        for r in c["references"]:
            if r not in used:
                used.append(r)
    key = "".join('<li id="%s"><strong>%s</strong> <span>%s</span></li>' % (src_id(r), esc(r), esc(REVIEW_SOURCES.get(r, ""))) for r in used)
    secs.append('<section class="tool-sec" aria-labelledby="sources"><h2 id="sources"><span class="tool-sec__code">Key</span>Sources <span class="tool-sec__tag">\u2014 what each \u201cBased on\u201d label refers to</span></h2><ul class="src-key">%s</ul></section>' % key)
    write("readiness-review.html", tool_page("AI Readiness Review", "A 27-criterion readiness review for AI features, with screening questions and references to the EU AI Act, NIST, ISO/IEC 42001, WCAG 2.2, and HAX/PAIR guidelines.", "review", intro, "".join(secs), note))


# ---------------------------------------------------------------- simple pages
def build_changelog():
    items = ""
    for e in sorted(CHANGELOG, key=lambda x: x["date"], reverse=True):
        links = " ".join('<a href="%s">%s</a>' % (esc(l["href"]), esc(l["label"])) for l in e.get("links", []))
        items += '<li><time datetime="%s">%s</time><p>%s %s</p></li>' % (e["date"], fmt_date(e["date"]), esc(typo(e["text"])), links)
    body = """<main id="main" class="page">
  <header class="page__head"><p class="eyebrow">Record</p><h1>Changelog</h1>
  <p class="page__lede">What changed on this site and when. Corrections and revisions to a law also appear in that law's revision history.</p></header>
  <ol class="changelog">%s</ol>
  <p class="page__note"><a href="feed.xml">RSS feed</a></p>
</main>""" % items
    write("changelog.html", layout("Changelog", "What changed on Laws of AI Evaluation, and when.", body, current="changelog"))


def build_about():
    body = """<main id="main" class="page page--prose">
  <header class="page__head"><p class="eyebrow">About</p><h1>About this guide</h1>
  <p class="page__lede">An independent reference for people who build, buy, or design with AI. It collects the reliable ways AI evaluation goes wrong, with the research behind each one.</p></header>
  <section><h2 id="what-a-law-is">What a \u201claw\u201d means here</h2>
  <p>A law here is a reliable pattern with research behind it, not a law of physics. Some have established names, like Goodhart\u2019s Law. Others are named on this site to make a well-documented idea easier to remember, and each page says which.</p></section>
  <section><h2 id="editorial-policy">Editorial policy</h2>
  <ul>
    <li>Every law links to its sources. Preprints, reports, working papers, and books are labeled as such. Everything else is peer-reviewed or a classic in its field.</li>
    <li>Each law shows when its evidence was last checked and carries a version number and revision history.</li>
    <li>The <a href="changelog.html">Changelog</a> records what changed and when. Corrections are made in the open.</li>
    <li>Role tags, plain-terms summaries, checklist questions, and claim-checker rules are editorial work built from the laws themselves. They are starting points, not authority.</li>
  </ul></section>
  <section><h2 id="who">Who maintains it</h2>
  <p>Maintained by <a href="https://josephalfonso.com">Joseph Alfonso</a>, a UX design lead. To suggest a correction or a source, use the <a href="https://josephalfonso.com/pages/contact.html">contact page</a>.</p></section>
  <section><h2 id="how-to-use">How to use it</h2>
  <p>Start with the <a href="guide.html">guide</a>, browse the <a href="index.html">laws</a>, or paste a claim into the <a href="claim-checker.html">claim checker</a> to see which laws apply. Collect any laws with the Add buttons to get a <a href="brief.html">quick brief</a>, or turn them into a printable sheet with the <a href="checklist.html">checklist builder</a>.</p></section>
</main>"""
    write("about.html", layout("About", "About Laws of AI Evaluation: what a law means here, the editorial policy, and who maintains it.", body, current="about"))


def guide_nav(active):
    items = "".join('<li><a href="%s"%s>%s</a></li>' % (href, ' aria-current="page"' if href == active else "", label) for href, label in GUIDE_PAGES)
    return '<nav class="guide-nav" aria-label="Guide sections"><ul>%s</ul></nav>' % items


def guide_page(fname, title, eyebrow, desc, lede, blocks_html, extra=""):
    body = """<main id="main" class="page page--prose">
  %s
  <header class="page__head"><p class="eyebrow">%s</p><h1>%s</h1>%s</header>
  %s%s
</main>""" % (guide_nav(fname), esc(eyebrow), esc(title), lede, blocks_html, extra)
    write(fname, layout(title, desc, body, current=None))


def build_guide_pages():
    overview = manuscript_region("## AI Evaluation, an Overview", "## The Laws")
    guide_page(
        "guide.html",
        "AI Evaluation, an Overview",
        "How to use this guide",
        "What AI evaluation is, why it is hard, and how to use the laws.",
        "",
        md_blocks(overview),
    )
    pragmatic = manuscript_region("## Being Pragmatic", "## Field Guide")
    guide_page("being-pragmatic.html", "Being Pragmatic", "Guide", "How to do AI evaluation inside a real team with deadlines, limited budget, and a model that changed last Tuesday.", "", md_blocks(pragmatic))

    field = manuscript_region("## Field Guide", "## Glossary")
    # split the eval card template out of the regular flow
    start = next(i for i, l in enumerate(field) if l.startswith("### 4"))
    end = next(i for i, l in enumerate(field) if i > start and l.startswith("### References"))
    card_lines = [l for l in field[start + 1 : end]]
    card_rows = []
    seen_marker = False
    for l in card_lines:
        t = l.strip().replace("&nbsp;", "").strip()
        if t == "EVAL CARD":
            seen_marker = True
            continue
        if not seen_marker:
            continue
        if l.strip() == "&nbsp;":
            card_rows.append('<hr class="evalcard__sep">')
        elif t:
            card_rows.append('<p class="evalcard__row">%s</p>' % inline(t))
    card = '<div class="evalcard" role="group" aria-label="Eval card template"><p class="evalcard__title">Eval card</p>%s</div>' % "".join(card_rows)
    before = md_blocks(field[:start])
    after = md_blocks(field[end:])
    guide_page("field-guide.html", "Field Guide", "Guide", "Questions for reading an AI claim, a sequence for building your own eval, red flags, and an eval card template.", "", before + '<h2 id="4-eval-card-template">4. Eval card template</h2><p>Copy this into any eval you run. It borrows from model cards (Mitchell et al., 2019).</p>' + card + after)

    gl = "".join('<div class="gloss__row"><dt id="%s">%s</dt><dd>%s%s</dd></div>' % (
        slugify(g["term"]), esc(typo(g["term"])), inline(g["definition"]),
        (" See " + ", ".join(link_laws(inline(n)) for n in g["see"]) + ".") if g["see"] else "") for g in GLOSS)
    guide_page("glossary.html", "Glossary", "Guide", "Definitions of the terms used across the laws.", "", '<dl class="gloss">%s</dl>' % gl)

    bib_lines = manuscript_region("## Bibliography", "\u0000end")
    entries, cur = [], None
    for ln in bib_lines:
        if ln.startswith("- "):
            cur = {"ref": ln[2:].rstrip(), "cited": ""}
            entries.append(cur)
        elif ln.strip().startswith("Cited in:") and cur is not None:
            cur["cited"] = ln.strip()[len("Cited in:") :].strip()
    intro = next((l for l in bib_lines if l.strip() and not l.startswith("-")), "")
    items = ""
    for e in entries:
        cited = []
        rest = e["cited"]
        for n, s in NAMES:
            if n in rest:
                cited.append('<a href="laws/%s.html">%s</a>' % (s, esc(typo(n))))
                rest = rest.replace(n, "")
        for label, href in PAGE_LINKS.items():
            if label in rest:
                cited.append('<a href="%s">%s</a>' % (href, label))
        items += '<li class="bib__item"><span>%s</span><span class="bib__cited">Cited in: %s</span></li>' % (inline(e["ref"]), ", ".join(cited))
    guide_page("bibliography.html", "Bibliography", "Guide", "Every source cited on this site.", '<p class="page__lede">%s</p>' % inline(intro), '<ul class="bib">%s</ul>' % items)


# ---------------------------------------------------------------- claim checker, checklist
def build_claim_checker():
    types = EDIT["claimChecker"]["types"]
    chips = "".join('<button type="button" class="chip-toggle" data-type="%s" aria-pressed="false">%s</button>' % (t["id"], esc(t["label"])) for t in types)
    rules = ""
    for t in types:
        rows = "".join("<li><a href=\"%s\">%s</a> <span class=\"rules__fit\">%s</span> %s</li>" % (law_url(r["slug"]), esc(typo(BY_SLUG[r["slug"]]["name"])), {"strong": "strong match", "likely": "likely", "worth": "worth checking"}[r["fit"]], esc(typo(r["why"]))) for r in t["laws"])
        rules += "<h3>%s</h3><ul>%s</ul>" % (esc(t["label"]), rows)
    body = """<main id="main" class="page page--claim" data-page="claim">
  <div class="claim">
    <section class="claim__input" aria-labelledby="claim-h">
      <p class="eyebrow eyebrow--muted">Tool</p>
      <h1 id="claim-h">Check a claim</h1>
      <p class="page__lede">Paste a claim about an AI system. You get the laws that apply, why, and a question to ask for each.</p>
      <label class="field-label" for="claim-text">The claim</label>
      <textarea id="claim-text" class="claim__text" rows="5" placeholder="Our assistant scores 94%% on MMLU-Pro and beats leading models on our internal benchmark."></textarea>
      <p class="field-label field-label--row" id="type-label">What kind of claim? <span class="muted-inline" data-detect-note>Detected from the text, edit if wrong</span></p>
      <div class="chip-toggles" role="group" aria-labelledby="type-label">%s</div>
      <div class="claim__buttons"><button class="btn btn--accent" type="button" data-find>Find laws that apply</button><button class="btn btn--outline" type="button" data-export disabled>Export questions</button><button class="btn btn--ghost" type="button" data-example>Try an example</button></div>
      <p class="claim__note">Matching is rule-based against the laws\u2019 published criteria. <a href="#how-matching-works">How matching works</a></p>
    </section>
    <section class="claim__results" aria-live="polite" aria-labelledby="results-h" data-results>
      <h2 id="results-h" class="visually-hidden">Results</h2>
      <p class="claim__empty">Results appear here. Paste a claim and choose Find laws that apply.</p>
    </section>
  </div>
  <section class="claim__rules" id="how-matching-works"><h2>How matching works</h2>
    <p>Each claim type maps to the laws a careful reader would check first, using the manuscript\u2019s Field Guide and red-flag table. A few phrases (such as \u201cinternal benchmark\u201d or \u201csuperhuman\u201d) add matches of their own. A law that matches more than one type moves up a step. This is a reading aid, not an assessment of the claim.</p>
    <details><summary>Show the rules</summary>%s</details>
  </section>
</main>""" % (chips, rules)
    write("claim-checker.html", layout("Claim checker", "Paste a claim about an AI system and see which laws apply, why, and what to ask.", body, current="claim", data=True, scripts=("claim-checker.js",)))


def build_brief():
    body = """<main id="main" class="page page--brief" data-page="brief">
  <header class="page__head"><p class="eyebrow eyebrow--muted">Learn</p><h1>Quick brief</h1>
  <p class="page__lede">Pick any laws and get a short overview you can read in a few minutes. It links to the full law pages and their sources.</p></header>
  <details class="brief__picker no-print" data-brief-picker><summary data-picker-summary>Choose laws</summary>
    <div class="brief__presets" data-brief-presets></div>
    <div class="picker" data-brief-grid></div></details>
  <div class="brief__out" data-brief-out></div>
  <noscript><p class="page__note">The quick brief needs JavaScript. You can read each law on the <a href="index.html">laws page</a> instead.</p></noscript>
  <p class="page__note">Assembled in your browser from each law\u2019s own text. The plain-terms summaries were drafted with AI and are starting points: read the full law and its sources before you rely on one.</p>
</main>"""
    write("brief.html", layout("Quick brief", "Pick any laws and get a short overview you can read in a few minutes, built from each law's own text.", body, current="laws", data=True, scripts=("brief.js",)))


def build_checklist():
    body = """<main id="main" class="page page--checklist" data-page="checklist">
  <div class="checklist-controls no-print">
    <p class="eyebrow eyebrow--muted">Tool</p>
    <h1>Build a printable checklist</h1>
    <p class="page__lede">Pick a starting set of laws, adjust it, and print or save a one-sheet checklist with the questions to ask.</p>
    <div class="seg seg--rule seg--wrap" role="group" aria-label="Preset" data-presets></div>
    <details class="customise" data-customise><summary data-customise-summary>Customise laws</summary><div class="customise__grid" data-law-grid></div></details>
    <button class="btn btn--ink btn--lg" type="button" data-print>Print / save PDF</button>
    <p class="muted-inline" data-empty hidden>Select at least one law to build a checklist.</p>
  </div>
  <section class="sheet" data-sheet aria-label="Checklist preview"></section>
</main>"""
    write("checklist.html", layout("Checklist builder", "Build a printable checklist of questions to ask when evaluating an AI system.", body, current="laws", data=True, scripts=("checklist.js",)))


# ---------------------------------------------------------------- emitted data
def build_data_js():
    nums = {l["slug"]: l["no"] for l in LAWS}
    presets = {}
    for key, p in EDIT["presets"].items():
        if key.startswith("_"):
            continue
        presets[key] = {"label": p["label"], "laws": [l["no"] for l in LAWS] if p["laws"] == "all" else sorted(nums[s] for s in p["laws"])}
    brief_presets = [{"id": "tour", "label": EDIT["briefPresets"]["tour"]["label"], "laws": sorted(nums[x] for x in EDIT["briefPresets"]["tour"]["laws"])}]
    for key in ("buying", "building", "launch"):
        brief_presets.append({"id": key, "label": presets[key]["label"], "laws": presets[key]["laws"]})
    data = {
        "site": {"baseUrl": SITE["baseUrl"], "version": SITE["version"], "updated": SITE["updated"]},
        "categories": [{"id": c["id"], "name": c["name"], "n": c["n"], "thread": c["thread"]} for c in CATS],
        "laws": [
            {
                "no": l["no"], "slug": l["slug"], "name": l["name"], "aphorism": l["aphorism"], "cat": l["category"], "questions": l["questions"],
                "plain": typo(l["plainTerms"]), "evidence": l["evidenceLine"], "doIt": l["doIt"], "shared": l["shared"],
            }
            for l in LAWS
        ],
        "presets": presets,
        "briefPresets": brief_presets,
        "claim": {
            "types": [{"id": t["id"], "label": t["label"], "detect": t["detect"], "laws": [dict(r, no=nums[r["slug"]]) for r in t["laws"]]} for t in EDIT["claimChecker"]["types"]],
            "modifiers": [dict(m, no=nums[m["slug"]]) for m in EDIT["claimChecker"]["modifiers"]],
        },
    }
    write("js/data.js", "/* Generated by build/build.py. Do not edit. */\nwindow.LAI = %s;\n" % json.dumps(data, ensure_ascii=False, separators=(",", ":")))


def build_search_index():
    entries = []
    for l in LAWS:
        u = "laws/%s.html" % l["slug"]
        entries.append({"k": "Law", "n": l["no"], "t": l["name"], "s": l["aphorism"], "u": u})
        sections = [
            ("takeaways", "Takeaways", " ".join(plain(t) for t in l["takeaways"])),
            ("what-it-means", "What it means", " ".join(plain(t) for t in l["whatItMeans"])),
            ("the-evidence", "The evidence", " ".join(plain(e["lead"] + " " + e["text"]) for e in l["evidence"])),
            ("use-it", "Use it", " ".join(plain(t) for t in l["useIt"])),
            ("origins", "Origins", " ".join(plain(t) for t in l["origins"])),
        ]
        for sid, label, text in sections:
            entries.append({"k": "Section", "n": l["no"], "t": "%s \u203a %s" % (l["name"], label), "x": text, "u": "%s#%s" % (u, sid)})
    for g in RUBRIC:
        for it in g["items"]:
            entries.append({"k": "Rubric", "n": it["id"], "t": it["text"], "s": "%s \u00b7 %s" % (g["name"], g["tagline"]), "u": "design-rubric.html#%s" % it["id"]})
    dims = {d["code"]: d["title"] for d in AIRR["dimensions"]}
    for c in AIRR["criteria"]:
        entries.append({"k": "Review", "n": c["id"], "t": c["criterion"], "s": "%s \u00b7 %s" % (dims[c["dimension"]], ", ".join(c["references"])), "u": "readiness-review.html#%s" % c["id"]})
    for e in CHANGELOG:
        entries.append({"k": "Changelog", "n": fmt_date(e["date"], short=True), "t": e["text"], "u": "changelog.html"})
    write("js/search-index.js", "/* Generated by build/build.py. Do not edit. */\nwindow.LAI_SEARCH = %s;\n" % json.dumps(entries, ensure_ascii=False, separators=(",", ":")))


def build_feed():
    items = ""
    for e in sorted(CHANGELOG, key=lambda x: x["date"], reverse=True):
        d = datetime.date.fromisoformat(e["date"])
        pub = d.strftime("%a, %d %b %Y 00:00:00 +0000")
        items += "<item><title>%s</title><link>%s/changelog</link><guid isPermaLink=\"false\">%s-%s</guid><pubDate>%s</pubDate><description>%s</description></item>\n" % (
            esc(e["text"]), SITE["baseUrl"], e["date"], hashlib.md5(e["text"].encode("utf-8")).hexdigest()[:8], pub, esc(e["text"]))
    feed = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>%s: changelog</title><link>%s/</link><description>What changed on %s.</description>\n%s</channel></rss>\n' % (
        esc(SITE["title"]), SITE["baseUrl"], esc(SITE["title"]), items)
    write("feed.xml", feed)


def main():
    build_index()
    for i, law in enumerate(LAWS):
        build_law(i, law)
    build_rubric()
    build_review()
    build_changelog()
    build_about()
    build_guide_pages()
    build_claim_checker()
    build_checklist()
    build_brief()
    build_data_js()
    build_search_index()
    build_feed()
    print("built: %d laws, %d pages" % (len(LAWS), len(list(ROOT.glob("*.html"))) + len(LAWS)))


if __name__ == "__main__":
    main()
